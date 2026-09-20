#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "ImageIO.hpp"

namespace py = pybind11;
using namespace mps;

PYBIND11_MODULE(mps_engine, m) {
    m.doc() = "MiniPhotoshop C++ engine";

    py::class_<Image>(m, "Image")
        .def(py::init<>())
        .def_readonly("width", &Image::width)
        .def_readonly("height", &Image::height)
        .def_readonly("channels", &Image::channels)
        .def("empty", &Image::empty)
        .def("to_numpy", [](const Image& img) {
            // buat numpy array shape (height, width) buat grayscale
            // atau (height, width, channels) buat RGB
            if (img.channels == 1) {
                return py::array_t<uint8_t>(
                    {img.height, img.width},
                    img.data.data()
                );
            } else {
                return py::array_t<uint8_t>(
                    {img.height, img.width, img.channels},
                    img.data.data()
                );
            }
        });
    
    //PGM
    m.def("load_pgm", [](const string& filename) {
        Image img;
        bool ok = loadPGM(filename, img);
        return py::make_tuple(ok, img);
    }, "Load citra PGM. Return (success, Image)");

    m.def("save_pgm", &savePGM, "Simpan citra ke file PGM",
          py::arg("filename"), py::arg("img"), py::arg("binary") = true);

    //PPM
    m.def("load_ppm", [](const string& filename) {
        Image img;
        bool ok = loadPPM(filename, img);
        return py::make_tuple(ok, img);
    }, "Load citra PPM. Return (success, Image)");

    m.def("save_ppm", &savePPM, "Simpan citra ke file PPM",
          py::arg("filename"), py::arg("img"), py::arg("binary") = true);

    //PBM
    m.def("load_pbm", [](const string& filename) {
        Image img;
        bool ok = loadPBM(filename, img);
        return py::make_tuple(ok, img);
    }, "Load citra PBM. Return (success, Image)");

    m.def("save_pbm", &savePBM, "Simpan citra ke file PBM",
          py::arg("filename"), py::arg("img"), py::arg("binary") = true);

    //RAW
    m.def("load_raw", [](const string& filename){
        Image img;
        bool ok= loadRAW(filename, img);
        return py::make_tuple(ok, img);
    }, "Load citra RAW. Return (success, Image)");

    m.def("save_raw", &saveRAW, "Simpan citra ke file RAW",
        py::arg("filename"), py::arg("img"));
}