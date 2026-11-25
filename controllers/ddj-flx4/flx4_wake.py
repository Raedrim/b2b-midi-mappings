"""Wake-up only: keeps the DDJ-FLX4 awake for the direct preset (no pad modes, no lights).

Run this BEFORE B2B Studio and leave it open. For pad modes and lights use flx4_bridge.py instead.
"""
import time
import mido

# Pioneer DDJ-FLX4 wake-up / keep-alive SysEx payload (without F0/F7 framing)
WAKE_BYTES = [0x00, 0x40, 0x05, 0x00, 0x00, 0x04, 0x05, 0x00, 0x50, 0x02]

port_name = next((p for p in mido.get_output_names() if "DDJ-FLX4" in p), None)
if not port_name:
    raise RuntimeError("DDJ-FLX4 not found. Close rekordbox/MIDI-OX and reconnect USB.")

with mido.open_output(port_name) as outport:
    print(f"Keeping {port_name} awake. Leave this window open while using B2B Studio...")
    while True:
        outport.send(mido.Message("sysex", data=WAKE_BYTES))
        time.sleep(2)