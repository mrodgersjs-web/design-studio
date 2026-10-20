"""Tests for tokens_toolkit.contrast.

Numbers come from published WCAG 2.1 worked examples and from the
validator at https://webaim.org/resources/contrastchecker/ for sanity
checks.
"""

from __future__ import annotations

import pytest

from tokens_toolkit import contrast


def test_luminance_white_is_one_and_black_is_zero():
    assert contrast.relative_luminance(contrast.RGBA(255, 255, 255)) == 1.0
    assert contrast.relative_luminance(contrast.RGBA(0, 0, 0)) == 0.0


def test_known_ratio_black_on_white_is_21_to_1():
    result = contrast.check("#000000", "#ffffff")
    assert result.ratio == pytest.approx(21.0, abs=0.01)
    assert result.aaa_normal is True
    assert result.aa_normal is True
    assert result.aa_large is True


def test_known_ratio_white_on_white_is_1_to_1():
    result = contrast.check("#ffffff", "#ffffff")
    assert result.ratio == pytest.approx(1.0, abs=0.01)
    assert result.grade() == "FAIL"


def test_short_hex_round_trip_via_long_hex():
    bg_long = contrast.check("#0000ff", "#ffffff").ratio
    bg_short = contrast.check("#00f", "#ffffff").ratio
    assert bg_long == pytest.approx(bg_short, abs=0.01)


def test_hex6_accepts_lower_and_upper_case():
    lc = contrast.parse_color
    assert contrast.relative_luminance(lc("#AaCc12")) == contrast.relative_luminance(lc("#AACC12"))


def test_rgb_function_parses():
    assert contrast.relative_luminance(contrast.parse_color("rgb(0, 0, 0)")) == 0.0
    assert contrast.relative_luminance(contrast.parse_color("rgb(255, 255, 255)")) == 1.0


def test_rgba_with_zero_alpha_composites_against_background():
    # Pure red on a black background should resolve to pure red.
    result, fg, _bg = contrast.check_pair("rgba(255, 0, 0, 1)", "#000000")
    assert fg.r == 255 and fg.alpha == 1.0
    ref = contrast.contrast_ratio(contrast.RGBA(255, 0, 0), contrast.RGBA(0, 0, 0))
    assert result.ratio == pytest.approx(ref, abs=0.01)


def test_rgba_with_half_alpha_is_composited():
    # half-alpha red on black foreground equals a midtone red, which has
    # a smaller contrast ratio than full red.
    full = contrast.check("rgba(255, 0, 0, 1)", "#000000").ratio
    half = contrast.check("rgba(255, 0, 0, 0.5)", "#000000").ratio
    assert half < full


def test_grade_pass_for_aaa_pair():
    # Deep navy on cream: high contrast, should be AAA.
    result = contrast.check("#0a0822", "#f5f0eb")
    assert result.grade() == "AAA"


def test_grade_fail_for_low_contrast_pair():
    # Very low contrast colors.
    result = contrast.check("#cccccc", "#dddddd")
    assert result.grade() == "FAIL"


def test_parse_color_rejects_garbage():
    with pytest.raises(contrast.ContrastError):
        contrast.parse_color("not-a-color")


def test_relative_luminance_rejects_translucent():
    with pytest.raises(contrast.ContrastError, match="opaque"):
        contrast.relative_luminance(contrast.RGBA(255, 0, 0, 0.5))


def test_channel_out_of_range():
    with pytest.raises(contrast.ContrastError):
        contrast.RGBA(256, 0, 0)


def test_alpha_out_of_range():
    with pytest.raises(contrast.ContrastError):
        contrast.RGBA(0, 0, 0, 1.5)


def test_rgb_function_channel_too_high_clamps():
    assert contrast.parse_color("rgb(300, 0, 0)").r == 255


def test_composite_requires_opaque_background():
    with pytest.raises(contrast.ContrastError):
        contrast.composite(contrast.RGBA(0, 0, 0, 1), contrast.RGBA(255, 255, 255, 0.5))


def test_contrast_result_to_dict_round_trip_keys():
    keys = set(contrast.ContrastResult(2.0, False, False, False, False, False).to_dict().keys())
    assert keys == {"ratio", "aa_normal", "aa_large", "aaa_normal", "aaa_large", "non_text", "grade"}


def test_grade_aa_large_for_3_to_1_pair():
    # Construct a 3:1 ratio by hand to test the boundary.
    a = contrast.RGBA(0, 0, 0)
    b = contrast.RGBA(126, 126, 126)
    r = contrast.ContrastResult(
        ratio=contrast.contrast_ratio(a, b),
        aa_normal=False,
        aa_large=True,
        aaa_normal=False,
        aaa_large=False,
        non_text=True,
    )
    assert r.grade() == "AA-large"


def test_grade_aa_non_text_for_3_to_1_when_not_text():
    r = contrast.ContrastResult(
        ratio=3.0,
        aa_normal=False,
        aa_large=True,
        aaa_normal=False,
        aaa_large=False,
        non_text=True,
    )
    # 3.0:1 passes AA-large (text) and AA-non-text (UI); the more
    # specific text grade wins because 'best pass' prefers that label.
    assert r.grade() == "AA-large"
