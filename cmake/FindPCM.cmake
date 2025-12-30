find_path(PCM_INCLUDE_DIR
    NAMES cpucounters.h
    PATH_SUFFIXES pcm
    PATHS
        /usr
        /usr/local
        /opt
)

find_library(PCM_LIBRARY
    NAMES pcm
    PATHS
        /usr
        /usr/local
        /opt
)

include(FindPackageHandleStandardArgs)

find_package_handle_standard_args(
    PCM
    REQUIRED_VARS PCM_INCLUDE_DIR PCM_LIBRARY
    FAIL_MESSAGE "Intel PCM not found — please install it"
)

add_library(PCM::pcm UNKNOWN IMPORTED)

set_target_properties(PCM::pcm PROPERTIES
    IMPORTED_LOCATION ${PCM_LIBRARY}
    INTERFACE_INCLUDE_DIRECTORIES ${PCM_INCLUDE_DIR}
)
