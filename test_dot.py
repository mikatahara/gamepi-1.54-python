# Fill in line by line
import time
from gamepi_lcd import GamePiLCD

with GamePiLCD() as lcd:

    lcd.fill((0, 0, 0))
    time.sleep(2)

    for y in range(80,160):
        # Lines 0–79: Red
        lcd._set_window(0, y, 239, y)
        line = bytes([0x00, 0x7F]) * 240
        lcd.spi.writebytes(line)

        # Lines 80–159: Green
        lcd._set_window(0, y+80, 239, y+80)
        line = bytes([0xF8, 0x00]) * 240
        lcd.spi.writebytes(line)

        # Lines 160–239: Blue
        lcd._set_window(0, y+160, 239, y+160)
        line = bytes([0x07, 0x80]) * 240
        lcd.spi.writebytes(line)

    time.sleep(3)
