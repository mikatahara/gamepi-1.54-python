import time
from gamepi_lcd import GamePiLCD

with GamePiLCD() as lcd:

    # 全面黒
    lcd.fill((0, 0, 0))
    time.sleep(2)

    # 0～79行：赤
    x = 10
    for y in range(0,240,20):
        lcd.box(y, y, 10, 10, (255,0,0))
        time.sleep(0.5)

    for y in range(0,240,20):
        lcd.box(y, 240-y, 10, 10, (0,255,0))
        time.sleep(0.5)

    for y in range(0,240,20):
        lcd.box(y, 120, 10, 10, (0,0,255))
        time.sleep(0.5)