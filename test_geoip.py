"""Tests for cis_geoip (best-effort GeoIP locations for login notices).

The reader is stubbed throughout: the real GeoLite2-City database is a
50 MB download and never ships with the repo. describe() formatting and
failure behaviour are what's under test; the .mmdb decoder gets a small
hand-built buffer for its basic contract.
"""
import unittest

import cis_geoip


class _StubReader:
    def __init__(self, record=None, error=None):
        self.record = record
        self.error = error
        self.calls = []

    def lookup(self, ip_text):
        self.calls.append(ip_text)
        if self.error:
            raise self.error
        return self.record


def _record(city=None, region=None, country=None, registered=None):
    record = {}
    if city:
        record["city"] = {"names": {"en": city}}
    if region:
        record["subdivisions"] = [{"names": {"en": region}}]
    if country:
        record["country"] = {"names": {"en": country}}
    if registered:
        record["registered_country"] = {"names": {"en": registered}}
    return record


class DescribeTest(unittest.TestCase):
    def setUp(self):
        self.addCleanup(cis_geoip._reset_for_tests)

    def _install(self, reader):
        cis_geoip._READER = reader
        cis_geoip._READER_TRIED = True

    def test_full_location(self):
        self._install(_StubReader(_record("Tulum", "Quintana Roo", "Mexico")))
        self.assertEqual(
            cis_geoip.describe("45.178.73.84"), "Tulum, Quintana Roo, Mexico"
        )

    def test_missing_city(self):
        self._install(_StubReader(_record(None, "Quintana Roo", "Mexico")))
        self.assertEqual(cis_geoip.describe("45.178.73.84"), "Quintana Roo, Mexico")

    def test_country_only(self):
        self._install(_StubReader(_record(country="United States")))
        self.assertEqual(cis_geoip.describe("8.8.8.8"), "United States")

    def test_registered_country_fallback(self):
        self._install(_StubReader(_record(registered="Australia")))
        self.assertEqual(cis_geoip.describe("1.1.1.1"), "Australia")

    def test_repeated_part_dropped(self):
        self._install(_StubReader(_record("Singapore", "Singapore", "Singapore")))
        self.assertEqual(cis_geoip.describe("1.2.3.4"), "Singapore")

    def test_private_ip_has_no_location(self):
        stub = _StubReader(_record("Mesquite", "Texas", "United States"))
        self._install(stub)
        self.assertIsNone(cis_geoip.describe("192.168.1.118"))
        self.assertEqual(stub.calls, [])

    def test_loopback_and_empty(self):
        self._install(_StubReader(_record(country="United States")))
        self.assertIsNone(cis_geoip.describe("127.0.0.1"))
        self.assertIsNone(cis_geoip.describe(""))
        self.assertIsNone(cis_geoip.describe(None))

    def test_unknown_ip(self):
        self._install(_StubReader(None))
        self.assertIsNone(cis_geoip.describe("8.8.8.8"))

    def test_reader_error_never_raises(self):
        self._install(_StubReader(error=ValueError("corrupt db")))
        self.assertIsNone(cis_geoip.describe("8.8.8.8"))

    def test_no_database_no_location(self):
        cis_geoip._READER = None
        cis_geoip._READER_TRIED = True
        self.assertIsNone(cis_geoip.describe("8.8.8.8"))


class DecoderTest(unittest.TestCase):
    def test_map_of_strings(self):
        # map(1) { utf8(1) "a": utf8(1) "b" }
        buffer = bytes([0xE1, 0x41]) + b"a" + bytes([0x41]) + b"b"
        value, _ = cis_geoip._Decoder(buffer).decode(0)
        self.assertEqual(value, {"a": "b"})

    def test_uint_and_array(self):
        # array(2) [ uint16(300), utf8(2) "hi" ] -- array is extended type 11,
        # so its control byte is 0x02 followed by extended-type byte 0x04.
        buffer = bytes([0x02, 0x04, 0xA2, 0x01, 0x2C, 0x42]) + b"hi"
        value, _ = cis_geoip._Decoder(buffer).decode(0)
        self.assertEqual(value, [300, "hi"])

    def test_pointer(self):
        # At 0: pointer(1-byte) -> offset 5. At 5: utf8(3) "geo".
        buffer = bytes([0x20, 0x05, 0x00, 0x00, 0x00, 0x43]) + b"geo"
        value, _ = cis_geoip._Decoder(buffer, base=0).decode(0)
        self.assertEqual(value, "geo")


if __name__ == "__main__":
    unittest.main()
