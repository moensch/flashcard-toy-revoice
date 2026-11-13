# MicroPython preamble for the Pico: bit-banged SPI to a 25-series flash chip.
# The host tools prepend this to every job in tools/pico/ and run it with `mpremote run`.
#
#   chip pin 1 CS   -> GP17     chip pin 5 DI   -> GP19
#   chip pin 2 DO   -> GP16     chip pin 6 CLK  -> GP18
#   chip pin 3 WP   -> GP20     chip pin 7 HOLD -> GP21
#   chip pin 4 GND  -> GND      chip pin 8 VCC  -> 3V3
#
# WP and HOLD are driven high. In-circuit the toy's board already pulls them up and
# they can stay unconnected; on a loose chip they must be wired or the chip ignores us.
from machine import Pin
import time

cs = Pin(17, Pin.OUT, value=1)
sck = Pin(18, Pin.OUT, value=0)
mosi = Pin(19, Pin.OUT, value=0)
miso = Pin(16, Pin.IN, Pin.PULL_UP)
wp = Pin(20, Pin.OUT, value=1)
hold = Pin(21, Pin.OUT, value=1)
JEDEC_ID = b"\x85\x60\x13"          # Puya P25Q40H (sold as SY25Q40P), 512 KB


def send(byte):
    for i in range(7, -1, -1):
        mosi((byte >> i) & 1); sck(1); sck(0)


def recv_into(buf):
    s1 = sck.on; s0 = sck.off; m = miso.value
    for j in range(len(buf)):
        v = 0
        for _ in range(8):
            s1(); v = (v << 1) | m(); s0()
        buf[j] = v


def cmd_addr(c, a):
    mosi(0); cs(0)
    for b in (c, a >> 16, (a >> 8) & 255, a & 255):
        send(b)


def simple(c):
    mosi(0); cs(0); send(c); cs(1)


def read_id():
    b = bytearray(3); cs(0); send(0x9F); recv_into(b); cs(1)
    return bytes(b)


def read_into(addr, buf):
    cmd_addr(0x03, addr); recv_into(buf); cs(1)
