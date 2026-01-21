import struct
import math

from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame
from saleae.data import GraphTimeDelta


BITS_PER_FRAME = 80                  # 80 bits per LTC frame (including sync word)
SYNC_WORD      = 0b1011111111111100  # 16‑bit sync pattern
FRAMES_PER_SEC = {
    24:    24,
    25:    25,
    30:    30,
    29.97: 30,   # drop‑frame
}
DROP_FRAME_RATES = {29.97}



class LTCAnalyzer(HighLevelAnalyzer):

    def __init__(self):
        super().__init__()
        self._bit_buffer = []


    def decode(self, frame: AnalyzerFrame):

        self._bit_buffer.append(frame.data["data"])

        # Keep buffer size bounded to one frame (80 bits)
        if len(self._bit_buffer) > BITS_PER_FRAME:
            self._bit_buffer.pop(0)

        if len(self._bit_buffer) == BITS_PER_FRAME:
            return self._process_frame(frame.end_time)


    def _process_frame(self, timestamp):
        bits = self._bit_buffer

        # Convert list of bits (LSB first per LTC spec) to integer
        frame_int = 0
        for i, b in enumerate(bits):
            frame_int |= (b << i)

        # Extract the 16‑bit sync word (bits 64‑79, LSB first)
        sync = (frame_int >> 64) & 0xFFFF
        if sync != SYNC_WORD:
            return None

        # Decode BCD fields (see SMPTE 12‑M spec)
        def bcd(val, start, length):
            mask = (1 << length) - 1
            return (val >> start) & mask

        # Decode
        units   = bcd(frame_int, 0, 4)
        tens    = bcd(frame_int, 8, 2)
        frames  = units + (tens * 10)

        units   = bcd(frame_int, 16, 4)
        tens    = bcd(frame_int, 24, 3)
        seconds = units + (tens * 10)

        units   = bcd(frame_int, 32, 4)
        tens    = bcd(frame_int, 40, 3)
        minutes = units + (tens * 10)

        units   = bcd(frame_int, 48, 4)
        tens    = bcd(frame_int, 56, 2)
        hours   = units + (tens * 10)

        df_flag = (frame_int >> 10) & 1
        cf_flag = (frame_int >> 11) & 1

        tc = {
            "hours":   hours,
            "minutes": minutes,
            "seconds": seconds,
            "frames":  frames,
            "drop_frame": bool(df_flag),
            "color_frame": bool(cf_flag),
        }
        # Format as SMPTE string (e.g., 01:23:45:12 or 01:23:45;12 for DF)
        tc_str = self.smpte_to_str(tc)

        start_time = timestamp - GraphTimeDelta(millisecond=80*0.4) # Approximating start time conversatively to avoid overlaps
        end_time = timestamp
        self._bit_buffer = []

        return AnalyzerFrame('LTC', start_time, end_time, {
            'tc': tc_str
        })


    def smpte_to_str(self, tc):
        sep = ';' if tc.get("drop_frame") else ':'
        return f"{tc['hours']:02d}:{tc['minutes']:02d}:{tc['seconds']:02d}{sep}{tc['frames']:02d}"



