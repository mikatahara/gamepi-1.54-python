# Draw the boxes arranged side by side.
import time
from gamepi_lcd import GamePiLCD

with GamePiLCD() as lcd:

    lcd.fill((0, 0, 0))
    time.sleep(1)

    # y=x
    for x in range(0,240,20):
        lcd.box(x, x, 10, 10, (255,0,0))
        time.sleep(0.5)

    # y=-x
    for x in range(0,240,20):
        lcd.box(x, 240-x, 10, 10, (0,255,0))
        time.sleep(0.5)

    # y=120
    for x in range(0,240,20):
        lcd.box(x, 120, 10, 10, (0,0,255))
        time.sleep(0.5)