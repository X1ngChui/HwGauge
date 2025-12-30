# HwGauge/CMakeLists.txt: CMake configuration for HwGauge with NVML support
cmake_minimum_required(VERSION 3.25)

# Collect source files
file(GLOB_RECURSE HWGAUGE_SOURCES
    "${CMAKE_CURRENT_SOURCE_DIR}/*.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/*.cpp"
    "${CMAKE_CURRENT_SOURCE_DIR}/*.cxx"
    "${CMAKE_CURRENT_SOURCE_DIR}/*.cc"
)

file(GLOB_RECURSE HWGAUGE_HEADERS
    "${CMAKE_CURRENT_SOURCE_DIR}/*.h"
    "${CMAKE_CURRENT_SOURCE_DIR}/*.hpp"
    "${CMAKE_CURRENT_SOURCE_DIR}/*.hxx"
)

# Create executable target
add_executable(HwGauge ${HWGAUGE_SOURCES} ${HWGAUGE_HEADERS})

# Set target properties
set_target_properties(HwGauge PROPERTIES
    C_STANDARD 17
    C_STANDARD_REQUIRED ON
    C_EXTENSIONS OFF
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
    OUTPUT_NAME "hwgauge"
)

# Include directories
target_include_directories(HwGauge PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
)

# Add Intel PCM library
if(HWGAUGE_USE_INTEL_PCM)
endif()

# Add NVML library
if(HWGAUGE_USE_NVML)
    find_package(CUDAToolkit REQUIRED)
    target_link_libraries(HwGauge PRIVATE CUDA::nvml)
    target_compile_definitions(HwGauge PRIVATE HWGAUGE_USE_NVML=1)
endif()

# Add Intel PCM libraryc
if(HWGAUGE_USE_INTEL_PCM)
    set(PCM_INCLUDE_DIR "/usr/local/src/pcm/src")
    set(PCM_LIBRARY     "/usr/local/src/pcm/build/libpcm.so")

    message(STATUS "Using hard-coded PCM path:")
    message(STATUS "  include = ${PCM_INCLUDE_DIR}")
    message(STATUS "  library = ${PCM_LIBRARY}")

    if(NOT EXISTS ${PCM_LIBRARY})
        message(FATAL_ERROR "PCM library not found at ${PCM_LIBRARY}")
    endif()

    target_include_directories(HwGauge PRIVATE ${PCM_INCLUDE_DIR})
    target_link_libraries(HwGauge PRIVATE ${PCM_LIBRARY})
    target_compile_definitions(HwGauge PRIVATE HWGAUGE_USE_INTEL_PCM=1)

endif()

# Add spdlog library
target_link_libraries(HwGauge PRIVATE spdlog::spdlog)

# Add CLI11 library
target_link_libraries(HwGauge PRIVATE CLI11::CLI11)

# Add prometheus-cpp library
target_link_libraries(HwGauge PRIVATE prometheus-cpp::pull)