#!/usr/bin/env python3
"""
GamePi 1.54 / ST7789V 240x240 LCD driver
for Raspberry Pi Zero 2 W + Ubuntu/Linux.

Hardware:
    SPI0 MOSI : GPIO10
    SPI0 SCLK : GPIO11
    SPI0 CE0  : GPIO8
    DC        : GPIO25
    RESET     : GPIO27

This implementation uses Linux spidev + lgpio rather than the
old fbcp-ili9341 / /dev/mem implementation.

Install:
    sudo apt install python3-spidev python3-lgpio
"""

import time
import spidev
import lgpio
from PIL import Image


class GamePiLCD:
    WIDTH = 240
    HEIGHT = 320

    DC_PIN = 25
    RESET_PIN = 27

    # ST7789 commands
    SWRESET = 0x01
    SLPOUT = 0x11
    COLMOD = 0x3A
    MADCTL = 0x36
    DGMEN = 0xBA
    INVON = 0x21
    INVOFF = 0x20
    NORON = 0x13
    DISPON = 0x29
    CASET = 0x2A
    RASET = 0x2B
    RAMWR = 0x2C

    def __init__(self, spi_bus=0, spi_device=0, spi_speed_hz=32_000_000):
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)

        # ST7789 uses SPI mode 0.
        self.spi.mode = 0
        self.spi.max_speed_hz = spi_speed_hz
        self.spi.bits_per_word = 8

        # GPIO chip 0 contains GPIO25 and GPIO27 on the Raspberry Pi.
        self.gpio = lgpio.gpiochip_open(0)

        lgpio.gpio_claim_output(self.gpio, self.DC_PIN, 0)
        lgpio.gpio_claim_output(self.gpio, self.RESET_PIN, 1)

        self._reset()
        self._init_display()

    def _dc(self, value):
        lgpio.gpio_write(self.gpio, self.DC_PIN, 1 if value else 0)

    def _reset(self):
        # Same basic reset timing as fbcp-ili9341:
        # high -> low -> high, 120 ms each.
        lgpio.gpio_write(self.gpio, self.RESET_PIN, 1)
        time.sleep(0.120)

        lgpio.gpio_write(self.gpio, self.RESET_PIN, 0)
        time.sleep(0.120)

        lgpio.gpio_write(self.gpio, self.RESET_PIN, 1)
        time.sleep(0.120)

    def _command(self, command, *data):
        """Send one ST7789 command followed by optional data."""
        self._dc(0)
        self.spi.writebytes([command])

        if data:
            self._dc(1)
            self.spi.writebytes([x & 0xff for x in data])

    def _init_display(self):
        # The original fbcp-ili9341 initializes the display at
        # a deliberately low SPI speed before changing to the
        # requested operating speed.
        old_speed = self.spi.max_speed_hz
        self.spi.max_speed_hz = min(old_speed, 1_000_000)

        # ST7789 (not ST7789VW): Software Reset
        self._command(self.SWRESET)
        time.sleep(0.120)

        # Sleep Out
        self._command(self.SLPOUT)
        time.sleep(0.120)

        # Gamma Curve Select
        self._command(0x26, 0x04)

        # Pixel format: 16 bit
        self._command(self.COLMOD, 0x05)
        time.sleep(0.020)

        # The supplied fbcp-ili9341 source sends 0xC0 for MADCTL.
        self._command(self.MADCTL, 0xC0)
        time.sleep(0.010)

        # ST7789 gamma enable
        self._command(self.DGMEN, 0x04)

        # Display inversion ON
        self._command(self.INVON)

        # Normal display mode
        self._command(self.NORON)
        time.sleep(0.010)

        # Display ON
        self._command(self.DISPON)
        time.sleep(0.100)

        self.spi.max_speed_hz = old_speed

        self.fill((0, 0, 0))

    def _set_window(self, x0, y0, x1, y1):
        """Set the ST7789 drawing window."""
        self._command(
            self.CASET,
            (x0 >> 8) & 0xff, x0 & 0xff,
            (x1 >> 8) & 0xff, x1 & 0xff
        )

        self._command(
            self.RASET,
            (y0 >> 8) & 0xff, y0 & 0xff,
            (y1 >> 8) & 0xff, y1 & 0xff
        )

        # RAM write command. Data follows with DC high.
        self._dc(0)
        self.spi.writebytes([self.RAMWR])
        self._dc(1)

    @staticmethod
    def _rgb888_to_rgb565(image):
        """Convert PIL RGB image to big-endian RGB565 bytes."""
        rgb = image.convert("RGB")
        src = rgb.load()

        data = bytearray(len(rgb.width * [0]) if False else rgb.width * rgb.height * 2)
        p = 0

        for y in range(rgb.height):
            for x in range(rgb.width):
                r, g, b = src[x, y]

                value = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

                # ST7789 expects the high byte first.
                data[p] = (value >> 8) & 0xff
                data[p + 1] = value & 0xff
                p += 2

        return data

    def show(self, image):
        """Display a PIL Image. Image is resized to 240x240 if necessary."""
        if image.size != (self.WIDTH, self.HEIGHT):
            image = image.resize((self.WIDTH, self.HEIGHT))

        data = self._rgb888_to_rgb565(image)

        self._set_window(0, 0, self.WIDTH - 1, self.HEIGHT - 1)

        # writebytes() has practical transfer-size limits on some
        # Linux setups, so send the frame in chunks.
        chunk_size = 4096

        for start in range(0, len(data), chunk_size):
            self.spi.writebytes(data[start:start + chunk_size])

    def fill(self, color):
        """Fill the entire LCD with an RGB tuple, e.g. (255, 0, 0)."""
        image = Image.new("RGB", (self.WIDTH, self.HEIGHT), color)
        self.show(image)

    def box(self, x, y, width, height, color):
        """Draw a square."""
        r, g, b = color
        value = (
            ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        )
        pixel = bytes([(value >> 8) & 0xff,value & 0xff])

        # Drawing area
        y = y + 80      #Hight offdet
        x1 = x + width - 1
        y1 = y + height - 1

        self._set_window(x, y, x1, y1)

        # 1 pixel × width
        line = pixel * width

        # Send one line's worth of bytes 'hight' times.
        for _ in range(height):
            self.spi.writebytes(line)

    def hline(self, y, color):
        """Draw a horizontal line."""
        r, g, b = color
        value = (
            ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        )
        pixel = bytes([(value >> 8) & 0xff,value & 0xff])
        # 1 pixel × 240 columns wide
        line = pixel * self.WIDTH

        self._set_window(0, y+80, self.WIDTH-1, y+80)
        self.spi.writebytes(line)

    def vline(self, x, color):
        """Draw a vertical line."""
        r, g, b = color
        value = (
            ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        )
        pixel = bytes([(value >> 8) & 0xff,value & 0xff])
        height = self.HEIGHT - 80
        # 1 pixel × 240 lines in height
        data = pixel * height

        self._set_window(x, 80, x, self.HEIGHT - 1)
        self.spi.writebytes(data)

    def close(self):
        """Release SPI and GPIO resources."""
        try:
            self.spi.close()
        finally:
            try:
                lgpio.gpiochip_close(self.gpio)
            except Exception:
                pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


if __name__ == "__main__":
    # Simple test:
    #   sudo python3 gamepi_lcd.py
    #
    # The screen should become red.
    with GamePiLCD() as lcd:
        lcd.fill((255, 0, 0))
        time.sleep(3)
