<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: Copyright 2025 Sam Blenny -->
# Fruit Jam Color Gradient

This generates a rainbow swirl color palette for a smooth range of saturated
hues that have approximately the same luminance value. The goal here is to make
a palette for Metro RP2350 or Fruit Jam that will work for animations with a
color swirl effect. This code is meant for the picodvi 320x240 16-bit video
mode with an 8-bit bitmap using a palette of 256 colors selected from the 65536
possible colors of RGB565.

This code was developed and tested on CircuitPython 10.0.0-alpha.7 with a Metro
RP2350 (no PSRAM version) and a pre-release revision B Fruit Jam prototype.
Keep in mind that things may change by the time CircuitPython 10.0.0 is
released.


## Video Mode Board Compatibility

It seems like you need a board with a PSRAM chip in order to use 640x480 with
8-bit color depth. The 320x240 8-bit and 16-bit modes are more reliable. This
table summarizes the results of my video mode testing for the boards I had on
hand:

| Video Mode     | Fruit Jam | Metro RP2350 No PSRAM    |
| -------------- | --------- | ------------------------ |
| (320, 240,  8) | Yes!      | Yes!                     |
| (320, 240, 16) | Yes!      | Yes!                     |
| (320, 240, 32) | Yes!      | MemoryError exception :( |
| (640, 480,  8) | Yes!      | MemoryError exception :( |
