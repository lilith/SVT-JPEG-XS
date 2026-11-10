/*
* Copyright(c) 2024 Intel Corporation
* SPDX - License - Identifier: BSD - 2 - Clause - Patent
*/
#include "gtest/gtest.h"
#include "SvtJpegxsEnc.h"

namespace {
svt_jpeg_xs_encoder_api_t configuration() {
    svt_jpeg_xs_encoder_api_t enc;
    EXPECT_EQ(svt_jpeg_xs_encoder_load_default_parameters(SVT_JPEGXS_API_VER_MAJOR, SVT_JPEGXS_API_VER_MINOR, &enc),
              SvtJxsErrorNone);
    enc.verbose = VERBOSE_NONE;
    enc.source_width = 256;
    enc.source_height = 256;
    enc.input_bit_depth = 8;
    enc.colour_format = COLOUR_FORMAT_PLANAR_YUV422;
    enc.bpp_numerator = 3;
    enc.bpp_denominator = 1;
    enc.coding_raw_disable = 1;
    enc.ndecomp_v = 1;
    return enc;
}

SvtJxsErrorType_t initialize(svt_jpeg_xs_encoder_api_t enc) {
    const auto result = svt_jpeg_xs_encoder_init(SVT_JPEGXS_API_VER_MAJOR, SVT_JPEGXS_API_VER_MINOR, &enc);
    // Close both successful and partially initialized instances.
    svt_jpeg_xs_encoder_close(&enc);
    return result;
}

void expect_conflict(svt_jpeg_xs_encoder_api_t enc) {
    enc.strict_stream_declarations = 0;
    EXPECT_EQ(initialize(enc), SvtJxsErrorNone);
    enc.strict_stream_declarations = 1;
    EXPECT_EQ(initialize(enc), SvtJxsErrorBadParameter);
}
} // namespace

TEST(StrictStreamDeclarations, DefaultsPreserveLegacyOverrides) {
    auto enc = configuration();
    EXPECT_EQ(enc.strict_stream_declarations, 0u);
    // Main 422.10 cannot describe per-packet raw-mode selection or two vertical levels.
    enc.profile_ppih_override = 0x3540;
    enc.coding_raw_disable = 0;
    enc.ndecomp_v = 2;
    expect_conflict(enc);
}

TEST(StrictStreamDeclarations, ProfilePrecisionAndSliceRestrictions) {
    auto enc = configuration();
    enc.profile_ppih_override = 0x3540;
    enc.input_bit_depth = 12;
    expect_conflict(enc);
    enc.input_bit_depth = 8;
    enc.slice_height = 8;
    expect_conflict(enc);
}

TEST(StrictStreamDeclarations, UnknownProfileAndLevelCodes) {
    auto enc = configuration();
    enc.profile_ppih_override = 0x1234;
    expect_conflict(enc);
    enc.profile_ppih_override = 0;
    enc.level_plev_override = 0x0c00;
    expect_conflict(enc);
    enc.level_plev_override = 0x0405; // Unknown sublevel.
    expect_conflict(enc);
    enc.level_plev_override = 0x0500; // FBB level on a non-TDC stream.
    expect_conflict(enc);
}

TEST(StrictStreamDeclarations, DimensionAndRateBoundary) {
    auto enc = configuration();
    enc.source_width = 1280;
    enc.source_height = 512;
    enc.level_plev_override = 0x0404; // 1k-1, 3 bpp.
    enc.fps_numerator = 255;
    enc.fps_denominator = 2;
    enc.strict_stream_declarations = 1;
    // 1280 * 512 * 255/2 = 83,558,400 grid points/s, exactly the 1k-1 limit.
    EXPECT_EQ(initialize(enc), SvtJxsErrorNone);
    enc.fps_numerator = 256;
    expect_conflict(enc);
    enc.fps_numerator = 0;
    enc.source_width = 1282;
    expect_conflict(enc);
}

TEST(StrictStreamDeclarations, RoundedFrameByteBoundary) {
    auto enc = configuration();
    enc.strict_stream_declarations = 1;
    enc.bpp_numerator = 2;
    enc.source_width = 258;
    enc.source_height = 257;
    enc.level_plev_override = 0x0403; // 1k-1, 2 bpp.
    // 258 * 257 * 2 = 132612 bits; rounded frame is 16577 bytes = 132616 bits.
    expect_conflict(enc);
    enc.level_plev_override = 0x0404; // 3 bpp covers the four rounding bits.
    EXPECT_EQ(initialize(enc), SvtJxsErrorNone);
    enc.source_width = 256;
    enc.source_height = 256;
    enc.level_plev_override = 0x0403; // Exact byte boundary remains legal.
    EXPECT_EQ(initialize(enc), SvtJxsErrorNone);
}

TEST(StrictStreamDeclarations, UnknownClockRemainsAnExternalAssertion) {
    auto enc = configuration();
    enc.strict_stream_declarations = 1;
    enc.level_plev_override = 0x0404;
    EXPECT_EQ(initialize(enc), SvtJxsErrorNone);
    // Unknown timing cannot justify automatic level selection, but is not a proven conflict.
    enc.fps_denominator = 0;
    EXPECT_EQ(initialize(enc), SvtJxsErrorNone);
}

TEST(StrictStreamDeclarations, LosslessCannotGuaranteeBoundSublevel) {
    auto enc = configuration();
    enc.lossless_enable = 1;
    enc.level_plev_override = 0x0410; // 12 bpp.
    expect_conflict(enc);
    enc.strict_stream_declarations = 1;
    enc.level_plev_override = 0x0400; // No byte bound.
    EXPECT_EQ(initialize(enc), SvtJxsErrorNone);
}

TEST(StrictStreamDeclarations, FullNeedsNamedProfileAndBoundsBytes) {
    auto enc = configuration();
    enc.input_bit_depth = 9;          // Automatic profile is Unrestricted.
    enc.level_plev_override = 0x0480; // Full needs a named profile.
    expect_conflict(enc);
    enc.input_bit_depth = 8;
    enc.profile_ppih_override = 0x3540; // Full for Main 422.10 is 20 bpp.
    enc.bpp_numerator = 20;
    enc.strict_stream_declarations = 1;
    EXPECT_EQ(initialize(enc), SvtJxsErrorNone);
    enc.bpp_numerator = 21;
    expect_conflict(enc);
}

TEST(StrictStreamDeclarations, StaticLightChecksDoNotClaimBufferCertification) {
    auto enc = configuration();
    enc.strict_stream_declarations = 1;
    for (uint16_t profile : {0x1500, 0x1a00, 0x2500}) {
        enc.profile_ppih_override = profile;
        enc.ndecomp_v = profile == 0x2500 ? 0 : 1;
        EXPECT_EQ(initialize(enc), SvtJxsErrorNone);
    }
}

TEST(StrictStreamDeclarations, InvalidPolicyValueIsRejected) {
    auto enc = configuration();
    enc.strict_stream_declarations = 2;
    EXPECT_EQ(initialize(enc), SvtJxsErrorBadParameter);
}
