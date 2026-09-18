import time
from gamepi_lcd import GamePiLCD


with GamePiLCD() as lcd:
    lcd.fill((0, 0, 0))
    time.sleep(0.5)

    # 1行ずつ赤色を送る
    for y in range(80):
        # y行だけを描画領域に設定
        lcd.hline(y, (255,0,0))
        time.sleep(0.02)

    for y in range(80,160):
        # y行だけを描画領域に設定
        lcd.hline(y, (0,255,0))
        time.sleep(0.02)

    for y in range(160,240):
        # y行だけを描画領域に設定
        lcd.hline(y, (0,0,255))
        time.sleep(0.02)

    time.sleep(1)

    lcd.fill((0, 0, 0))
    time.sleep(0.5)

    # 1列ずつ赤色を送る
    for x in range(80):
        # y行だけを描画領域に設定
        lcd.vline(x, (255,0,0))
        time.sleep(0.02)

    for x in range(80,160):
        # y行だけを描画領域に設定
        lcd.vline(x, (0,255,0))
        time.sleep(0.02)

    for x in range(160,240):
        # y行だけを描画領域に設定
        lcd.vline(x, (0,0,255))
        time.sleep(0.02)

