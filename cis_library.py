"""Library file transfer persistence helpers."""

import shutil
import cis_communities
from cis_web_files import offer_download
from pathlib import Path


GENERATED_DOCUMENTS = {
    "IRQNOTE.TXT": """IBM PC INTERRUPT REQUEST NOTES - DECEMBER 1988

IRQ 3  COM2 or COM4
IRQ 4  COM1 or COM3
IRQ 5  Often available on PC/XT systems
IRQ 6  Floppy disk controller
IRQ 7  Parallel printer adapter

Two devices normally should not share an interrupt. Consult the adapter manual before changing jumpers.
""",
    "MODEMREF.TXT": """HAYES-COMPATIBLE MODEM COMMAND SUMMARY

ATZ       Reset modem
ATDT      Dial using touch tones
ATDP      Dial using pulses
ATH       Hang up
ATS0=1    Answer after one ring
AT&F      Recall factory configuration when supported

Command availability varies by manufacturer. Keep the modem manual nearby.
""",
    "MEMORY.TXT": """DOS MEMORY NOTES

Conventional memory occupies the first 640K address space. Device drivers and resident programs reduce the memory available to applications. CONFIG.SYS and AUTOEXEC.BAT should load only required software. Expanded memory requires a compatible board and manager.
""",
    "RS232.TXT": """RS-232 QUICK REFERENCE

Pin 2 Transmitted Data   Pin 3 Received Data
Pin 4 Request To Send    Pin 5 Clear To Send
Pin 6 Data Set Ready     Pin 7 Signal Ground
Pin 8 Carrier Detect     Pin 20 Data Terminal Ready

Verify whether equipment is wired as DTE or DCE before selecting a cable.
""",
    "CONFIG.TXT": """CONFIG.SYS NOTES

FILES=20 increases the number of simultaneously open files.
BUFFERS=20 reserves disk buffers.
DEVICE= loads a device driver during startup.

Make one change at a time and keep a bootable system diskette nearby.
""",
    "AUTOEXEC.TXT": """AUTOEXEC.BAT NOTES

PATH selects directories searched for commands. PROMPT $P$G displays the current drive and directory. MODE configures communications and display devices. Avoid unnecessary resident programs when an application requires additional conventional memory.
""",
    "VGAINFO.TXT": """VGA DISPLAY NOTES

The Video Graphics Array introduced with IBM PS/2 systems supports 640 by 480 monochrome graphics and 320 by 200 graphics with 256 colors from a larger palette. Software and monitor compatibility should be verified before purchase.
""",
    "EMSNOTE.TXT": """EXPANDED MEMORY NOTES

LIM EMS uses a page frame in upper memory to map portions of expanded memory into the processor address space. Applications must explicitly support EMS. Board switches and the memory manager must agree on the selected addresses.
""",
    "TERM10.TXT": """TERMLINK 1.0 SHAREWARE RELEASE NOTES

Terminal capture and dialing-directory demonstration. Known issue: systems using COM2
may conflict with another adapter assigned to IRQ3. Record current settings before use.
This simulated text package contains no executable software.
""",
    "TERM11.TXT": """TERMLINK 1.1 CORRECTED SHAREWARE RELEASE NOTES

Adds explicit COM1/COM2 selection, startup conflict warnings, and expanded modem setup
notes. Thanks to IBM Hardware Forum testers. This simulated text package contains no
executable software.
""",
}


def materialize_download(app, file, protocol):
    download_dir = app.BASE_DIR / "downloads"
    download_dir.mkdir(exist_ok=True)
    destination = download_dir / Path(file["name"]).name
    stored_path = file.get("stored_path")
    community_content = cis_communities.download_content(file)
    if stored_path and (app.BASE_DIR / stored_path).exists():
        shutil.copy2(app.BASE_DIR / stored_path, destination)
    elif community_content is not None:
        destination.write_bytes(community_content.encode('ascii'))
        file['bytes'] = destination.stat().st_size
    elif file["name"] in GENERATED_DOCUMENTS:
        destination.write_text(GENERATED_DOCUMENTS[file["name"]], encoding="ascii", errors="replace")
        file["bytes"] = destination.stat().st_size
    else:
        heading = (f'CompuServe IBMHW Library File #{file["number"]}\r\n{file["name"]}\r\n{file["description"]}\r\n').encode("ascii", errors="replace")
        destination.write_bytes((heading + b"\x1a" * file["bytes"])[:file["bytes"]])
    file["downloads"] += 1
    app.save_json_atomic("library_files.json", app.library_files)
    if getattr(app, "current_user_id", None):
        app.cis_dynamic.record_activity(app, app.current_user_id, "LIBRARY", f'Downloaded {file["name"]} using {protocol}.', {"number": file["number"], "protocol": protocol})
    offer_download(destination)
    return destination
