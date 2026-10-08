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

    //transformasi log
    m.def("log_transform", [](Image& img){
        logTransform(img);
        return img;
    }, "Transformasi log (in-place, return citra yang sama)", py::arg("img"));
    
    //inverse log
    m.def("inverse_log_transform", [](Image& img){
        inverseLogTransform(img);
        return img;
    }, "Transformasi inverse log (in-place, return citra yang sama)", py::arg("img"));

    //transformasi pangkat
    m.def("power_transform", [](Image& img, double gamma, double c){
        powerTransform(img, gamma, c);
        return img;
    }, "Transformasi pangkat (in-place, return citra yang sama)", py::arg("img"), py::arg("gamma"), py::arg("c") = 1.0);

    //contrast stretching (manual)
    m.def("contrast_stretching", [](Image& img, int r1, int s1, int r2, int s2){
        if(r1 < 0 || r2 > 255 || s1 < 0 || s2 > 255 || r1 > r2){
            throw py::value_error("syarat: 0 <= r1 <= r2 <= 255, 0 <= s1, s2 <= 255");
        }
        contrastStretching(img, r1, s1, r2, s2);
        return img;
    },
    "Contrast stretching garis patah lewat (r1,s1) dan (r2,s2) (in-place, return citra yang sama)",
    py::arg("img"), py::arg("r1"), py::arg("s1"), py::arg("r2"), py::arg("s2"));

    //contrast stretching (otomatis)
    m.def("auto_contrast_stretching", [](Image& img, double a, double b){
        if(a < 0.0 || b > 100.0 || a >= b){
            throw py::value_error("syarat: 0 <= a < b <= 100");
        }
        autoContrastStretching(img, a, b);
        return img;
    },
    "Contrast stretching otomatis dari histogram; a% tergelap jadi hitam, (100-b)% terterang jadi putih (in-place, return citra yang sama)",
    py::arg("img"), py::arg("a") = 1.0, py::arg("b") = 99.0);

    //gray-level slicing
    m.def("gray_slicing", [](Image& img, int a, int b, bool preserve, int highlight, int background){
        graySlicing(img, a, b, preserve, highlight, background);
        return img;
    }, "Gray-level slicing rentang [a,b] jadi highlight; preserve=True pertahankan latar, False latar jadi background (in-place, return citra yang sama)",
        py::arg("img"), py::arg("a"), py::arg("b"), py::arg("preserve") = false, py::arg("highlight") = 255, py::arg("background") = 0);

    //bit-plane slicing
    m.def("bit_plane_slicing", [](Image& img, int k, bool binary){
        if(k < 0 || k > 7){
            throw py::value_error("k harus 0..7");
        }
        bitPlaneSlicing(img, k, binary);
        return img;
    }, "Ambil bit-plane ke-k (0=LSB, 7=MSB); binary=True: bit 1->255, bit 0->0; False: nilai kontribusi bit (in-place, return citra yang sama)",
        py::arg("img"), py::arg("k"), py::arg("binary") = true);

    //perataan histogram (equalization)
    m.def("equalize_histogram", &equalizeHistogram);

    //smoothing: mean filter
    m.def("mean_filter", [](Image& img, int ksize){
        meanFilter(img, ksize);
        return img;
    }, "Smoothing mean filter ksize x ksize (in-place, return citra yang sama)",
       py::arg("img"), py::arg("ksize") = 3);

    //smoothing: gaussian filter
    m.def("gaussian_filter", [](Image& img, int ksize, double sigma){
        gaussianFilter(img, ksize, sigma);
        return img;
    }, "Gaussian filter (in-place, return citra yang sama)",
       py::arg("img"), py::arg("ksize") = 3, py::arg("sigma") = 1.0);

    //smoothing: median filter
    m.def("median_filter", [](Image& img, int ksize){
        medianFilter(img, ksize);
        return img;
    }, "Smoothing median filter ksize x ksize (in-place, return citra yang sama)",
       py::arg("img"), py::arg("ksize") = 3);

    //edge detection: sobel
    m.def("sobel_filter", [](Image& img, int mode){
        sobelFilter(img, mode);
        return img;
    }, "Deteksi tepi sobel (in-place, return citra yang sama); mode=0: |Gx|+|Gy|, 1: max, 2: akar kuadrat, 3: rata-rata",
       py::arg("img"), py::arg("mode") = 0);

    //noise: salt & pepper
    m.def("add_salt_pepper", [](Image& img, double prob, unsigned int seed){
        addSaltPepper(img, prob, seed);
        return img;
    }, "Tambahkan noise salt & pepper (in-place, return citra yang sama)",
       py::arg("img"), py::arg("prob") = 0.01, py::arg("seed") = 0);

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