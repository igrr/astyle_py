cmake_minimum_required(VERSION 3.15)

if(NOT DEFINED ENV{EMSDK_PATH})
    message(FATAL_ERROR "EMSDK_PATH environment variable not set")
endif()

if(NOT DEFINED ASTYLE_VER)
    message(FATAL_ERROR "ASTYLE_VER cache variable not set")
endif()

set(CMAKE_TOOLCHAIN_FILE $ENV{EMSDK_PATH}/upstream/emscripten/cmake/Modules/Platform/Emscripten.cmake)

set(BUILD_STATIC_LIBS 1 CACHE BOOL "Build static libraries")

project(astyle-wasm)

include(FetchContent)
FetchContent_Declare(
    astyle
    GIT_REPOSITORY https://gitlab.com/saalen/astyle.git
    GIT_TAG ${ASTYLE_VER}
)
FetchContent_MakeAvailable(astyle)


add_executable(astyle-wasm wrapper.c)
target_link_libraries(astyle-wasm PRIVATE astyle)

target_link_libraries(astyle-wasm PRIVATE "-s EXPORTED_FUNCTIONS=[\"_AStyleGetVersion\",\"_AStyleWrapper\",\"_malloc\",\"_free\",\"_AStyleErrorHandler\"]")
target_link_libraries(astyle-wasm PRIVATE "-s STANDALONE_WASM=1")
target_link_libraries(astyle-wasm PRIVATE "-s ERROR_ON_UNDEFINED_SYMBOLS=0")
target_link_libraries(astyle-wasm PRIVATE "-s WARN_ON_UNDEFINED_SYMBOLS=1")
target_link_libraries(astyle-wasm PRIVATE --no-entry)
target_link_libraries(astyle-wasm PRIVATE -Wl,--import-undefined)
