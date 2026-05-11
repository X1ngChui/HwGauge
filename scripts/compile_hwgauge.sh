#!/bin/bash
set -euo pipefail

# Default options
USE_PCM="OFF"
USE_NVML="OFF"

# Parse arguments
for arg in "$@"; do
  case $arg in
    intel_pcm) USE_PCM="ON" ;;
    nvml)      USE_NVML="ON" ;;
  esac
done

# Check if at least one component is enabled
if [ "$USE_PCM" == "OFF" ] && [ "$USE_NVML" == "OFF" ]; then
    echo "No components selected. Available components: intel_pcm, nvml"
    echo "Usage: $0 [intel_pcm] [nvml]"
    exit 1
fi

# 1. Install build tools
sudo apt update
sudo apt install -y build-essential cmake ninja-build

# 2. Clone repository
rm -rf HwGauge
git clone https://github.com/X1ngChui/HwGauge.git --recursive

# 3. Build
cd HwGauge/

# Disable tests in pcm vendor to avoid conflicts
if [ -f "vendors/pcm/CMakeLists.txt" ]; then
    sed -i 's/^[[:blank:]]*add_subdirectory(tests)/# &/' vendors/pcm/CMakeLists.txt
fi

mkdir -p build && cd build

# Configure with CMake options
cmake .. -G Ninja \
    -DHWGAUGE_USE_INTEL_PCM=$USE_PCM \
    -DHWGAUGE_USE_NVML=$USE_NVML

# Build target
cmake --build . --target hwgauge --parallel

# 4. Copy binary
if [ -f "bin/hwgauge" ]; then
    cp bin/hwgauge ../../
else
    exit 1
fi

# 5. Clean up
cd ../..
rm -rf HwGauge
