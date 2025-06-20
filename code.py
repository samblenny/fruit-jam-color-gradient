# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2025 Sam Blenny
from board import CKP, CKN, D0P, D0N, D1P, D1N, D2P, D2N
import displayio
from displayio import Bitmap, Group, Palette, TileGrid
import framebufferio
import gc
import math
import picodvi
import supervisor
from time import sleep


def make_gradient_palette():
    """Draw a color gradient (256 colors out of 65536 possible for RGB565).
    This makes a rainbow swirl of saturated hues with approximately the same
    luminance value.
    """
    p = Palette(256)
    # TODO: IMPLEMENT THIS
    return p

def draw_gradient(bitmap, palette):
    """Draw a color gradient using an 8-bit (256 position) palette"""
    # TODO: IMPLEMENT THIS
    pass

def init_display(width, height, color_depth):
    """Initialize the picodvi display
    Video mode compatibility (only tested these--unsure about other boards):
    | Video Mode      | Fruit Jam | Metro RP2350 No PSRAM    |
    | --------------- | --------- | ------------------------ |
    | 320x240, 8-bit  | Yes!      | Yes!                     |
    | 320x240, 16-bit | Yes!      | Yes!                     |
    | 640x480, 8-bit  | Yes!      | MemoryError exception :( |
    """
    displayio.release_displays()
    gc.collect()
    fb = picodvi.Framebuffer(width, height, clk_dp=CKP, clk_dn=CKN,
        red_dp=D0P, red_dn=D0N, green_dp=D1P, green_dn=D1N,
        blue_dp=D2P, blue_dn=D2N, color_depth=color_depth)
    display = framebufferio.FramebufferDisplay(fb)
    supervisor.runtime.display = display
    return display


# Attempt to configure display with the requested picodvi video mode
requested_mode = (320, 240, 16)
(width, height, color_depth) = requested_mode
display = supervisor.runtime.display
if (display is None) or (width, height) != (display.width, display.height):
    # Didn't find a display configured as we need, so initialize a new one
    print("re-initializing display for video mode", requested_mode)
    try:
        display = init_display(width, height, color_depth)
    except MemoryError as e:
        # Fall back to low resolution so the error message will be readable
        display = init_display(320, 240, 8)
        print("---\nREQUESTED VIDEO MODE NEEDS A BOARD WITH PSRAM\n---")
        raise e
else:
    print("using existing display for video mode", requested_mode)
display.auto_refresh = False

# Make a drawing canvas: bitmap + palette + tilegrid + group
palette = make_gradient_palette()
bitmap = Bitmap(width, height, 256)
tilegrid = TileGrid(bitmap, pixel_shader=palette)
grp = Group(scale=1)
grp.append(tilegrid)
display.root_group = grp

# Draw the gradient
draw_gradient(bitmap, palette)
display.refresh()

# Spin in a busy loop to prevent CircuitPython from clearing the screen
while True:
    sleep(1)
