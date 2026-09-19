cmake_minimum_required(VERSION 3.15)
project(miniphotoshop_engine)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(include)

#executable untuk testing manual
add_executable(
    mps_test
    src/main.cpp
    src/ImageIO_PGM.cpp
    src/ImageIO_PBM.cpp
)

#modul python via pybind11
find_package(pybind11 REQUIRED)
pybind11_add_module(
    mps_engine
    src/bindings.cpp
    src/ImageIO_PGM.cpp
    src/ImageIO_PBM.cpp
)
target_link_options(mps_engine PRIVATE -static-libgcc -static-libstdc++ -static -lwinpthread)