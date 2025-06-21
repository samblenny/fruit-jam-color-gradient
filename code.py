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
from ulab import numpy as np


def LCh_to_sRGB(L, C, h):
    """Convert L*C*h to gamma corrected sRGB color with D65 whitepoint.
    L*: perceptual Lightness in range 0-1.0 (this is related to luminance)
    C*: Chroma in range 0-1.0 (this is related to saturation)
    h: hue angle (range 0-360 degrees, 0=red, 90=yellow, 180=green, 270=blue)
    Returns:
    (R, G, B): tuple of red, green, and blue values in range 0-255
    Notes:
    - L*C*h color space uses polar coordinates to represent perceptual colors
      with an angle for hue
    - L*a*b* color space (CIELAB) is based on a standard model of human vision.
      The a* and b* values represent non-linear perceptual color and they can
      be negative.
    - XYZ color space is a transformed version of CIELAB where the values are
      linear and non-negative which makes some color math operations easier
    - Formulas are adapted from Bruce Lindbloom's color math pages at
      http://www.brucelindbloom.com/
    """
    # 1. Convert L*C*h to Lab (L stays the same).
    rh = math.radians(h)
    a = C * math.cos(rh)
    b = C * math.sin(rh)
    # 2. Convert L*a*b* (non-linear perceptual) to XYZ (linear).
    #    D65 reference white value: {X: 0.95047, Y: 1.0, Z: 1.08883}.
    #    The conditional values of (xr, yr, zr) using epsilon and k compensate
    #    for some aspects of the human eye's non-linear response to light.
    epsilon = 0.008856
    k = 903.3
    fy = (L + 16) / 116
    fx = (a / 500) + fy
    fz = fy - (b / 200)
    xr = fx ** 3
    if xr <= epsilon:
        xr = ((116 * fx) - 16) / k
    yr = ((L + 16) / 116) ** 3
    if L <= k * epsilon:
        yr = L / k
    zr = fz ** 3
    if zr <= epsilon:
        zr = ((116 * fz) - 16) / k
    XYZ = np.array([[xr * 0.95047], [yr * 1.00], [zr * 1.08883]])  # D65
    # 3. Convert XYZ to linear sRGB.
    #    M1 is the chromatic adaptation matrix for XYZ to sRGB with D65 white
    M = np.array([
        [ 3.2404542, -1.5371385, -0.4985314],
        [-0.9692660,  1.8760108,  0.0415560],
        [ 0.0556434, -0.2040259,  1.0572252]])
    RGB_linear = np.dot(M, XYZ)
    # 4. Apply sRGB gamma curve compensation
    compand = np.vectorize(lambda v:
        (12.92 * v) if (v <= 0.0031308) else (pow(1.055 * v, 1/2.4) - 0.055))
    RGB = compand(RGB_linear)
    # 5. Scale output range from 0-1.0 up to 0-255
    scale = np.vectorize(lambda v: min(255, max(0, v * 25500)))
    sRGB = tuple([int(n) for n in np.flip(scale(RGB))])
    return sRGB

def fill_gradient_palette(palette, L, C):
    """Make gradient palette with variable hue at fixed Lightness & Chroma"""
    palette[0] = (0, 0, 0)
    n = len(palette)
    for i in range(1, n):
        h = 360 * (i / (n-1))
        sRGB = LCh_to_sRGB(L, C, h)
        palette[i] = sRGB

def draw_gradient(bitmap, palette):
    """Draw a color gradient sample pattern using all the palette colors"""
    w = bitmap.width
    h = bitmap.height
    n = min(w, len(palette))
    x0 = (w - n) // 2
    y0 = h // 6
    for x in range(n):
        for y in range(h // 2):
            bitmap[x0 + x, y0 + y] = x

def init_display(width, height, color_depth):
    """Initialize the picodvi display
    Video mode compatibility (only tested these--unsure about other boards):
    | Video Mode     | Fruit Jam | Metro RP2350 No PSRAM    |
    | -------------- | --------- | ------------------------ |
    | (320, 240,  8) | Yes!      | Yes!                     |
    | (320, 240, 16) | Yes!      | Yes!                     |
    | (320, 240, 32) | Yes!      | MemoryError exception :( |
    | (640, 480,  8) | Yes!      | MemoryError exception :( |
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
#requested_mode = (320, 240, 32)
(width, height, color_depth) = requested_mode
try:
    display = init_display(width, height, color_depth)
except MemoryError as e:
    # Fall back to low resolution so the error message will be readable
    display = init_display(320, 240, 16)
    raise e
display.auto_refresh = False

# Make a drawing canvas: bitmap + palette + tilegrid + group
palette = Palette(256)
bitmap = Bitmap(width, height, 256)
tilegrid = TileGrid(bitmap, pixel_shader=palette)
grp = Group(scale=1)
grp.append(tilegrid)
display.root_group = grp

# Draw the gradient
draw_gradient(bitmap, palette)

# Cycle through palettes for a range of lightness and chroma values
while True:
    for C in range(2, 20, 1):
        for L in range(1, 5, 1):
            print("(L, C)", (L/10, C/10))
            fill_gradient_palette(palette, L/10, C/10)
            display.refresh()
            sleep(1)
