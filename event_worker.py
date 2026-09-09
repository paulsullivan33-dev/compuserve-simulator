"""Process due simulated events without starting an interactive terminal session."""

import cis_dynamic
import compuserve


if __name__ == "__main__":
    cis_dynamic.apply_clock_state(compuserve)
    changed = cis_dynamic.process_events(compuserve)
    print("Processed due CompuServe events." if changed else "No CompuServe events were due.")
