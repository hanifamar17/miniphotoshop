#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include "ImageIO.hpp"
#include "ImageProcessing.hpp"
#include "Histogram.hpp"

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
        .def("allocate", &Image::allocate, "Alokasi citra baru (width, height, channels)",
            py::arg("width"), py::arg("height"), py::arg("channels"))
        .def("clone", [](const Image& img) { return Image(img); }, "Buat salinan (deep copy) citra")
        .def("set_pixel", [](Image& img, int row, int col, int c, uint8_t value) {
            img.at(row, col, c)= value;
        }, "Set nilai piksel", py::arg("row"), py::arg("col"), py::arg("c"), py::arg("value"))
        .def("get_pixel", [](const Image& img, int row, int col, int c) {
            return img.at(row, col, c);
        }, "Ambil nilai piksel", py::arg("row"), py::arg("col"), py::arg("c")= 0)
        .def("to_numpy", [](const Image& img) {
            if (img.channels == 1) {
                return py::array_t<uint8_t>({img.height, img.width}, img.data.data());
            } else {
                return py::array_t<uint8_t>({img.height, img.width, img.channels}, img.data.data());
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

    //BMP
    m.def("load_bmp", [](const string& filename){
        Image img;
        bool ok= loadBMP(filename, img);
        return py::make_tuple(ok, img);
    }, "Load citra BMP. Return (success, Image)");

    m.def("save_bmp", &saveBMP, "Simpan citra ke file BMP",
        py::arg("filename"), py::arg("img"));

    //PNG
    m.def("load_png", [](const string& filename){
        Image img;
        bool ok= loadPNG(filename, img);
        return py::make_tuple(ok, img);
    }, "Load citra PNG. Return (success, Image)");

    m.def("save_png", &savePNG, "Simpan citra ke file PNG", py::arg("filename"), py::arg("img"));

    //JPG
    m.def("load_jpg", [](const string& filename){
        Image img;
        bool ok= loadJPG(filename, img);
        return py::make_tuple(ok, img);
    }, "Load citra JPG/JPEG. Return (success, Image)");

    m.def("save_jpg", &saveJPG, "Simpan citra ke file JPG", py::arg("filename"), py::arg("img"), py::arg("quality")=90);

    //OPERASI CITRA
    //konversi ke citra negatif
    m.def("make_negative", [](Image& img){
        makeNegative(img);
        return img;
    }, "Buat citra negatif (in-place, return citra yang sama)");

    //konversi RGB ke grayscale
    m.def("to_grayscale", [](const Image& img){
        Image result= toGrayscale(img);
        bool ok= !result.empty();
        return py::make_tuple(ok, result); 
    }, "Konversi citra RGB ke Grayscale. Return (success, Image)");

    //image brightening
    m.def("brighten", [](Image& img, int b){
        brighten(img, b);
        return img;
    }, "Ubah kecerahan citra (in-place, return citra yang sama)", py::arg("img"), py::arg("b"));

    //HiSTOGRAM
    py::class_<HistogramData>(m, "HistogramData")
        .def(py::init<>())
        .def_readonly("total_pixels", &HistogramData::totalPixels)
        .def_readonly("mean", &HistogramData::mean)
        .def_readonly("variance", &HistogramData::variance)
        .def_readonly("stdv", &HistogramData::stdv)
        .def_property_readonly("counts", [](const HistogramData& h){
            return vector<int>(h.counts, h.counts + 256);
        })
        .def_property_readonly("normalized", [](const HistogramData& h){
            return vector<double>(h.normalized, h.normalized + 256);
        });
    
    py::class_<ColorHistogramData>(m, "ColorHistogramData")
        .def(py::init<>())
        .def_readonly("red", &ColorHistogramData::red)
        .def_readonly("green", &ColorHistogramData::green)
        .def_readonly("blue", &ColorHistogramData::blue)
        .def_readonly("luminosity", &ColorHistogramData::luminosity);
       
    //histogram 1 channel
    m.def("compute_histogram", &computeHistogram, "Histogram citra 1 channel",
        py::arg("img"));
    
    //histogram 3 channel
    m.def("compute_color_histogram", &computeColorHistogram, "Histogram citra RGB (per kanal & luminosity)",
        py::arg("img"));
}