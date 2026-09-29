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

    //transformasi log
    void logTransform(Image& img);

    //inverse log
    void inverseLogTransform(Image& img);

    //transformasi pangkat
    void powerTransform(Image& img, double gamma, double c=1.0);

    //contrast stretching
    void contrastStretching(Image& img, int r1, int s1, int r2, int s2);
    void autoContrastStretching(Image& img, double a, double b);

    //gray-level slicing
    void graySlicing(Image& img, int a, int b, bool preserveBackground, int highlight = 255, int background = 0);

    //bit-plane slicing
    void bitPlaneSlicing(Image& img, int k, bool binary = true);
}