#pragma once
#include "Image.hpp"

namespace mps{
    //operasi Membuat citra negatif
    void makeNegative(Image& img);

    //konversi RGB ke grayscale
    Image toGrayscale(const Image& img);

    //image brightening
    //b+ = terang, b- = gelap
    void brighten(Image& img, int b);
}