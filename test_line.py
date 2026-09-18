# Fill in row by row, then clear the grid 
# and fill in column by column.
import time
from gamepi_lcd import GamePiLCD


with GamePiLCD() as lcd:
    lcd.fill((0, 0, 0))
    time.sleep(0.5)

    for y in range(80):
        # Lines 0–79: Red
        lcd.hline(y, (255,0,0))
        time.sleep(0.02)

    for y in range(80,160):
        # Lines 80–159: Green
        lcd.hline(y, (0,255,0))
        time.sleep(0.02)

    for y in range(160,240):
        # Lines 160–239: Blue
        lcd.hline(y, (0,0,255))
        time.sleep(0.02)

    time.sleep(1)

    # clear
    lcd.fill((0, 0, 0))
    time.sleep(0.5)

    for x in range(80):
        # Rows 0–79: Red
        lcd.vline(x, (255,0,0))
        time.sleep(0.02)

    for x in range(80,160):
        # Rows 80–159: Green
        lcd.vline(x, (0,255,0))
        time.sleep(0.02)

    for x in range(160,240):
        # Rows 160–239: Blue
        lcd.vline(x, (0,0,255))
        time.sleep(0.02)

