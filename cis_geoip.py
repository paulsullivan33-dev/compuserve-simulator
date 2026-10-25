"""Best-effort GeoIP locations for client IPs, from a local database.

Reads a MaxMind GeoLite2-City database (``GeoLite2-City.mmdb``) placed
next to this module, or wherever the CIS_GEOIP_DB environment variable
points. The location feeds the login notification in compuserve.py, so a
sysop can see at a glance where a session connected from.

Nothing here ever raises: a missing database, an unknown IP, or a
private address all produce None and the notification simply goes out
without a location, exactly as before. Only the standard library is
used -- the .mmdb reader below is a small read-only implementation of
the MaxMind DB file format (search tree plus data-section decoding),
which keeps the simulator's zero-dependency core intact.

The database itself is not shipped with the simulator (it is ~50 MB and
updates weekly). Fetch a fresh copy from MaxMind or a mirror, e.g.:

    curl -L -o GeoLite2-City.mmdb \
      https://github.com/P3TERX/GeoLite.mmdb/releases/latest/download/GeoLite2-City.mmdb

Locations describe where the connection appears to come from -- the
ISP's geography for that address block -- not where a person is. City
names are approximate; region and country are the reliable parts.
"""

import ipaddress
import mmap
import os
from pathlib import Path

_METADATA_MARKER = b"\xab\xcd\xefMaxMind.com"
_METADATA_SEARCH = 128 * 1024  # metadata lives within the last 128 KiB

# MaxMind DB data-section types.
_T_EXTENDED = 0
_T_POINTER = 1
_T_UTF8 = 2
_T_DOUBLE = 3
_T_BYTES = 4
_T_UINT16 = 5
_T_UINT32 = 6
_T_MAP = 7
_T_INT32 = 8
_T_UINT64 = 9
_T_UINT128 = 10
_T_ARRAY = 11
_T_BOOLEAN = 14
_T_FLOAT = 15


def database_path():
    """Where the GeoLite2-City database is expected to live."""
    override = os.environ.get("CIS_GEOIP_DB")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent / "GeoLite2-City.mmdb"


class _Decoder:
    """Decodes values from an .mmdb data section held in a buffer."""

    def __init__(self, buffer, base=0):
        self.buffer = buffer
        self.base = base  # file offset the section's pointers are relative to

    def decode(self, offset):
        """Return (value, next_offset) for the value at `offset`."""
        ctrl = self.buffer[offset]
        offset += 1
        type_id = ctrl >> 5
        size = ctrl & 0b11111
        if type_id == _T_EXTENDED:
            type_id = self.buffer[offset] + 7
            offset += 1
        if type_id == _T_POINTER:
            pointer, offset = self._pointer(size, offset)
            value, _ = self.decode(pointer)
            return value, offset
        if size == 29:
            size = 29 + self.buffer[offset]
            offset += 1
        elif size == 30:
            size = 285 + int.from_bytes(self.buffer[offset:offset + 2], "big")
            offset += 2
        elif size == 31:
            size = 65821 + int.from_bytes(self.buffer[offset:offset + 3], "big")
            offset += 3
        if type_id == _T_UTF8:
            return self.buffer[offset:offset + size].decode("utf-8"), offset + size
        if type_id == _T_BYTES:
            return bytes(self.buffer[offset:offset + size]), offset + size
        if type_id in (_T_UINT16, _T_UINT32, _T_UINT64, _T_UINT128):
            return int.from_bytes(self.buffer[offset:offset + size], "big"), offset + size
        if type_id == _T_INT32:
            return int.from_bytes(
                self.buffer[offset:offset + size], "big", signed=True
            ), offset + size
        if type_id == _T_DOUBLE:
            import struct

            return struct.unpack(">d", self.buffer[offset:offset + 8])[0], offset + 8
        if type_id == _T_FLOAT:
            import struct

            return struct.unpack(">f", self.buffer[offset:offset + 4])[0], offset + 4
        if type_id == _T_BOOLEAN:
            return bool(size), offset
        if type_id == _T_MAP:
            result = {}
            for _ in range(size):
                key, offset = self.decode(offset)
                value, offset = self.decode(offset)
                result[key] = value
            return result, offset
        if type_id == _T_ARRAY:
            result = []
            for _ in range(size):
                value, offset = self.decode(offset)
                result.append(value)
            return result, offset
        raise ValueError(f"unsupported .mmdb type {type_id}")

    def _pointer(self, size_bits, offset):
        size = ((size_bits >> 3) & 0b11) + 1
        base_value = size_bits & 0b111
        value = int.from_bytes(
            bytes([base_value]) + self.buffer[offset:offset + size], "big"
        )
        offset += size
        if size == 1:
            value += 0
        elif size == 2:
            value += 2048
        elif size == 3:
            value += 526336
        elif size == 4:
            # A fourth form stores the pointer in the following 4 bytes.
            value = int.from_bytes(self.buffer[offset:offset + 4], "big")
            offset += 4
        return self.base + value, offset


class _Reader:
    """A minimal read-only MaxMind DB reader over an mmap'ed file."""

    def __init__(self, path):
        self._file = open(path, "rb")
        self._buffer = mmap.mmap(self._file.fileno(), 0, access=mmap.ACCESS_READ)
        marker_at = self._buffer.rfind(
            _METADATA_MARKER, len(self._buffer) - _METADATA_SEARCH
        )
        if marker_at < 0:
            raise ValueError("no .mmdb metadata marker found")
        meta_start = marker_at + len(_METADATA_MARKER)
        metadata, _ = _Decoder(self._buffer, base=meta_start).decode(meta_start)
        self._node_count = metadata["node_count"]
        self._record_size = metadata["record_size"]
        self._ip_version = metadata["ip_version"]
        self._node_bytes = self._record_size // 4
        self._tree_size = self._node_count * self._node_bytes
        self._decoder = _Decoder(self._buffer, base=self._tree_size + 16)

    def _read_node(self, node, index):
        offset = node * self._node_bytes + index * (self._record_size // 8)
        if self._record_size == 24:
            return int.from_bytes(self._buffer[offset:offset + 3], "big")
        if self._record_size == 28:
            # The shared middle byte holds the HIGH nibble of each record.
            middle = self._buffer[node * self._node_bytes + 3]
            if index == 0:
                return ((middle >> 4) << 24) | int.from_bytes(
                    self._buffer[offset:offset + 3], "big"
                )
            return ((middle & 0x0F) << 24) | int.from_bytes(
                self._buffer[offset + 1:offset + 4], "big"
            )
        return int.from_bytes(self._buffer[offset:offset + 4], "big")

    def lookup(self, ip_text):
        """The record dict for `ip_text`, or None when it isn't in the DB."""
        address = ipaddress.ip_address(ip_text)
        if self._ip_version == 6 and isinstance(address, ipaddress.IPv4Address):
            address = ipaddress.IPv6Address(f"::ffff:{ip_text}")
        packed = address.packed
        node = 0
        for byte in packed:
            for shift in range(7, -1, -1):
                if node >= self._node_count:
                    break
                node = self._read_node(node, (byte >> shift) & 1)
            if node >= self._node_count:
                break
        if node == self._node_count:
            return None
        if node < self._node_count:
            return None  # ran out of bits without reaching data
        pointer = self._tree_size + (node - self._node_count)
        value, _ = self._decoder.decode(pointer)
        return value


_READER = None
_READER_TRIED = False


def _reader():
    """The shared reader, opened lazily; None when no database is present."""
    global _READER, _READER_TRIED
    if not _READER_TRIED:
        _READER_TRIED = True
        try:
            path = database_path()
            if path.is_file():
                _READER = _Reader(path)
        except Exception:
            _READER = None
    return _READER


def _reset_for_tests():
    global _READER, _READER_TRIED
    _READER = None
    _READER_TRIED = False


def lookup(ip_text):
    """The raw GeoIP record for an IP, or None. Never raises."""
    try:
        reader = _reader()
        if reader is None:
            return None
        return reader.lookup(ip_text)
    except Exception:
        return None


def describe(ip_text):
    """'City, Region, Country' for a public IP, or None. Never raises.

    Private, loopback, and otherwise non-global addresses have no
    meaningful location and return None, as do unknown addresses and
    any lookup problem.
    """
    try:
        if not ip_text:
            return None
        address = ipaddress.ip_address(ip_text)
        if not address.is_global:
            return None
        record = lookup(ip_text)
        if not record:
            return None
        city = (record.get("city") or {}).get("names", {}).get("en")
        country = (record.get("country") or {}).get("names", {}).get("en")
        if not country:
            # Anycast blocks (public DNS resolvers, say) often carry only
            # the country the block is registered in.
            country = (
                (record.get("registered_country") or {}).get("names", {}).get("en")
            )
        subdivisions = record.get("subdivisions") or []
        region = None
        if subdivisions:
            region = (subdivisions[-1] or {}).get("names", {}).get("en")
        parts = [part for part in (city, region, country) if part]
        # Drop a repeated part (e.g. city-state Singapore, or city == region).
        unique = []
        for part in parts:
            if part not in unique:
                unique.append(part)
        return ", ".join(unique) if unique else None
    except Exception:
        return None
