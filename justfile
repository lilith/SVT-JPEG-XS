# Build and run the declaration checks without external media.
configure-declarations:
    cmake -S . -B build-followup -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON -DBUILD_SHARED_LIBS=OFF -DJPEGXS_LTO=OFF

build-declarations: configure-declarations
    cmake --build build-followup -j4

test-declarations:
    Bin/Release/SvtJpegxsUnitTests --gtest_filter='StreamProfile*:StreamLevel*:ProfileLevelNames*:StrictStreamDeclarations*:VariousProfilesAndLevels/*'

# The caller selects the inventory; existing disabled/hardware-dependent cases keep their contracts.
test-units filter='*':
    Bin/Release/SvtJpegxsUnitTests --gtest_filter='{{filter}}'
