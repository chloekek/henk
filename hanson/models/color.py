# Hanson -- Self-hosted prediction market app
# Copyright 2023 Ruud van Asseldonk
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# A copy of the License has been included in the root of the repository.

from __future__ import annotations

from typing import NamedTuple, Tuple
import colorsys


Vec3 = Tuple[float, float, float]


def srgb_to_linear(v: float) -> float:
    """
    Map any rgb component of sRGB to linear RGB.
    Input and output are in the range [0, 1].
    """
    if v < 0.04045:
        return v / 12.92
    else:
        return ((v + 0.055) / 1.055) ** 2.4


def linear_to_srgb(v: float) -> float:
    """
    Inverse of `srgb_to_linear`.
    """
    if v < 0.0031308:
        return v * 12.92
    else:
        return (v ** (1 / 2.4)) * 1.055 - 0.055


def linear_rgb_to_xyz(r: float, g: float, b: float) -> Vec3:
    """
    Convert linear RGB to CIE XYZ.
    """
    x = 0.4124 * r + 0.3576 * g + 0.1805 * b
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = 0.0193 * r + 0.1192 * g + 0.9505 * b
    return x, y, z


def xyz_to_linear_rgb(x: float, y: float, z: float) -> Vec3:
    """
    Convert CIE XYZ to linear RGB.
    """
    # fmt: off
    r =  3.2406 * x - 1.5372 * y - 0.4986 * z
    g = -0.9689 * x + 1.8758 * y + 0.0415 * z
    b =  0.0557 * x - 0.2040 * y + 1.0570 * z
    # fmt: on
    return r, g, b


def xyz_to_cieluv(x: float, y: float, z: float) -> Vec3:
    """
    Convert CIE XYZ to CIELUV. Input values are in [0, 1], output values in
    [0, 100] for L* and [-100, 100] for u* and v*.
    """
    assert (x, y, z) != (0.0, 0.0, 0.0), "Cannot convert black."

    if y < (6 / 29) ** 3:
        l_s = ((29 / 3) ** 3) * y
    else:
        l_s = 116 * (y ** (1 / 3)) - 16

    u_p = 4 * x / (x + 15 * y + 3 * z)
    v_p = 9 * y / (x + 15 * y + 3 * z)
    u_pn = 0.2009
    v_pn = 0.4610

    u_s = 13 * l_s * (u_p - u_pn)
    v_s = 13 * l_s * (v_p - v_pn)

    return l_s, u_s, v_s


def cieluv_to_xyz(l_s: float, u_s: float, v_s: float) -> Vec3:
    """
    Convert CIELUV to CIE XYZ. Inverse of `xyz_to_cieluv`.
    """
    u_pn = 0.2009
    v_pn = 0.4610

    u_p = u_s / (13 * l_s) + u_pn
    v_p = v_s / (13 * l_s) + v_pn

    if l_s <= 8:
        y = l_s * (3 / 29) ** 3
    else:
        y = ((l_s + 16) / 116) ** 3

    x = y * (9 * u_p) / (4 * v_p)
    z = y * (12 - 3 * u_p - 20 * v_p) / (4 * v_p)

    return x, y, z


class Color(NamedTuple):
    # Color values ranging from 0 to 255.
    r: int
    g: int
    b: int

    @staticmethod
    def from_html_hex(hex: str) -> Color:
        """
        Parse a color that consists of six hexadecimal digits and the #,
        e.g. #ff0000.
        """

        assert hex.startswith("#")
        assert len(hex) == 7
        rgb = bytes.fromhex(hex[1:])
        return Color(rgb[0], rgb[1], rgb[2])

    def to_html_hex(self) -> str:
        """
        Format as # and six hexadecimal digits, e.g. #ff0000.
        """
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    def to_rgb_floats(self) -> Vec3:
        """
        Return a tuple with float rgb values in the range [0, 1].
        """
        return self.r / 255.0, self.g / 255.0, self.b / 255.0

    @staticmethod
    def from_rgb_floats(r: float, g: float, b: float) -> Color:
        """
        Create a color from floats between 0 and 1.
        """
        return Color(
            min(255, max(0, int(r * 255.0))),
            min(255, max(0, int(g * 255.0))),
            min(255, max(0, int(b * 255.0))),
        )

    def clamp_saturation(self, min_saturation: float, max_saturation: float) -> Color:
        h, l, s = colorsys.rgb_to_hls(*self.to_rgb_floats())
        s = min(max_saturation, max(min_saturation, s))
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return Color.from_rgb_floats(r, g, b)

    def clamp_lightness(self, min_lightness: float, max_lightness: float) -> Color:
        h, l, s = colorsys.rgb_to_hls(*self.to_rgb_floats())
        l = min(max_lightness, max(min_lightness, l))
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return Color.from_rgb_floats(r, g, b)
