cmake_minimum_required(VERSION 3.18)
project(PackageTest CXX)

set(CMAKE_CXX_STANDARD 17
    CACHE STRING "The C++ standard to use")
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(ace+tao CONFIG REQUIRED)

add_executable(package_test)
target_sources(package_test PRIVATE test_ace_tao_package.cpp)
target_compile_options(package_test PRIVATE  -Wall -Wextra -pedantic)

target_link_libraries(package_test PRIVATE ace+tao::ACE)
