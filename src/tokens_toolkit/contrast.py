"""WCAG 2.1 relative-luminance and contrast-ratio computation.

Pure-Python implementation of the formulas published at
https://www.w3.org/TR/WCAG21/#dfn-contrast-ratio and
https://www.w3.org/TR/WCAG21/#dfn-relative-luminance. No third-party
imports.

Color parsing accepts:

* ``#rgb``, ``#rrggbb``, ``#rrggbbaa`` (three-, six-, eight-digit hex)
* ``rgb(r, g, b)`` and ``rgba(r, g, b, a)`` (0..255 channels)

Anything else raises ``ContrastError``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

HEX3 = re.compile(r"^#([0-9a-fA-F]{3})$")
HEX6 = re.compile(r"^#([0-9a-fA-F]{6})$")
HEX8 = re.compile(r"^#([0-9a-fA-F]{8})$")
RGB_FN = re.compile(
    r"^rgba?\(\s*([0-9.]+)\s*,\s*([0-9.]+)\s*,\s*([0-9.]+)(?:\s*,\s*([0-9.]+))?\s*\)$"
)


class ContrastError(ValueError):
    """A color string cannot be parsed or the comparison is unusable."""


@dataclass(frozen=True)
class RGBA:
    r: int       # 0..255
    g: int       # 0..255
    b: int       # 0..255
    alpha: float = 1.0   # 0.0..1.0

    def __post_init__(self) -> None:
        for channel in (self.r, self.g, self.b):
            if not 0 <= channel <= 255:
                raise ContrastError(f"channel out of range: {channel}")
        if not 0.0 <= self.alpha <= 1.0:
            raise ContrastError(f"alpha out of range: {self.alpha}")


def parse_color(value: str) -> RGBA:
    """Parse a CSS color into an :class:`RGBA`."""
    if not isinstance(value, str):
        raise ContrastError(f"color must be a string; got {type(value).__name__}")
    text = value.strip()
    m = HEX6.match(text)
    if m:
        return _from_hex6(m.group(1))
    m = HEX3.match(text)
    if m:
        return _from_hex3(m.group(1))
    m = HEX8.match(text)
    if m:
        return _from_hex8(m.group(1))
    m = RGB_FN.match(text)
    if m:
        r = _clamp_byte(m.group(1))
        g = _clamp_byte(m.group(2))
        b = _clamp_byte(m.group(3))
        alpha = 1.0 if m.group(4) is None else _clamp_alpha(m.group(4))
        return RGBA(r, g, b, alpha)
    raise ContrastError(f"unrecognised color: {value!r}")


def _clamp_byte(text: str) -> int:
    try:
        value = float(text)
    except ValueError as exc:
        raise ContrastError(f"color channel not numeric: {text!r}") from exc
    rounded = round(value)
    if rounded < 0:
        return 0
    if rounded > 255:
        return 255
    return rounded


def _clamp_alpha(text: str) -> float:
    try:
        value = float(text)
    except ValueError as exc:
        raise ContrastError(f"color alpha not numeric: {text!r}") from exc
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def _from_hex3(hex3: str) -> RGBA:
    return _from_hex6("".join(ch * 2 for ch in hex3))


def _from_hex6(hex6: str) -> RGBA:
    return RGBA(
        int(hex6[0:2], 16),
        int(hex6[2:4], 16),
        int(hex6[4:6], 16),
        1.0,
    )


def _from_hex8(hex8: str) -> RGBA:
    return RGBA(
        int(hex8[0:2], 16),
        int(hex8[2:4], 16),
        int(hex8[4:6], 16),
        _clamp_alpha(str(int(hex8[6:8], 16) / 255)),
    )


def _channel_luminance(channel: int) -> float:
    """The sRGB relative-luminance transform for one channel in 0..255."""
    cs = channel / 255.0
    if cs <= 0.03928:
        return cs / 12.92
    return ((cs + 0.055) / 1.055) ** 2.4


def relative_luminance(color: RGBA) -> float:
    """The relative luminance per WCAG 2.1.

    Alpha is ignored for opaque foreground/background over a known background.
    """
    if color.alpha < 1.0:
        raise ContrastError("relative_luminance requires an opaque color")
    r = _channel_luminance(color.r)
    g = _channel_luminance(color.g)
    b = _channel_luminance(color.b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def composite(front: RGBA, back: RGBA) -> RGBA:
    """Composite an over-semi-transparent foreground onto an opaque background."""
    if back.alpha < 1.0:
        raise ContrastError("background must be opaque for compositing")
    a = front.alpha
    r = round(front.r * a + back.r * (1 - a))
    g = round(front.g * a + back.g * (1 - a))
    b = round(front.b * a + back.b * (1 - a))
    return RGBA(r, g, b, 1.0)


def contrast_ratio(foreground: RGBA, background: RGBA) -> float:
    """WCAG contrast ratio between two opaque colors."""
    l1 = relative_luminance(foreground)
    l2 = relative_luminance(background)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


@dataclass(frozen=True)
class ContrastResult:
    ratio: float
    aa_normal: bool        # 4.5:1
    aa_large: bool         # 3.0:1
    aaa_normal: bool       # 7.0:1
    aaa_large: bool        # 4.5:1
    non_text: bool         # 3.0:1 (UI components / graphical objects)

    def grade(self) -> str:
        if self.aaa_normal:
            return "AAA"
        if self.aa_normal:
            return "AA"
        if self.aa_large:
            return "AA-large"
        if self.non_text:
            return "AA-non-text"
        return "FAIL"

    def to_dict(self) -> dict:
        return {
            "ratio": round(self.ratio, 3),
            "aa_normal": self.aa_normal,
            "aa_large": self.aa_large,
            "aaa_normal": self.aaa_normal,
            "aaa_large": self.aaa_large,
            "non_text": self.non_text,
            "grade": self.grade(),
        }


def check(foreground: str, background: str) -> ContrastResult:
    """Compute the WCAG contrast result between two color strings.

    If ``foreground`` is translucent, it is composited onto ``background``
    first and the resulting opaque pair is graded.
    """
    front = parse_color(foreground)
    back = parse_color(background)
    if front.alpha < 1.0:
        front = composite(front, back)
    ratio = contrast_ratio(front, back)
    return ContrastResult(
        ratio=ratio,
        aa_normal=ratio >= 4.5,
        aa_large=ratio >= 3.0,
        aaa_normal=ratio >= 7.0,
        aaa_large=ratio >= 4.5,
        non_text=ratio >= 3.0,
    )


def check_pair(foreground: str, background: str) -> tuple[ContrastResult, RGBA, RGBA]:
    """Like :func:`check` but also returns the resolved RGBA pair (after compositing)."""
    front = parse_color(foreground)
    back = parse_color(background)
    if front.alpha < 1.0:
        front = composite(front, back)
    return check_against(front, back), front, back


def check_against(foreground: RGBA, background: RGBA) -> ContrastResult:
    ratio = contrast_ratio(foreground, background)
    return ContrastResult(
        ratio=ratio,
        aa_normal=ratio >= 4.5,
        aa_large=ratio >= 3.0,
        aaa_normal=ratio >= 7.0,
        aaa_large=ratio >= 4.5,
        non_text=ratio >= 3.0,
    )
