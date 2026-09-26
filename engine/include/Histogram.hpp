#pragma once
#include "Image.hpp"

namespace mps{
    struct HistogramData{
        int counts[256]= {0};
        double normalized[256]= {0.0};
        int totalPixels= 0;
        double mean= 0.0;
        double variance= 0.0;
        double stdv= 0.0;
    };

    struct ColorHistogramData{
        HistogramData red;
        HistogramData green;
        HistogramData blue;
        HistogramData luminosity;
    };

    //citra 1 channel (biner/gray)
    HistogramData computeHistogram(const Image& img);

    //citra 3 channel perkanal & gabungan (luminosity)
    ColorHistogramData computeColorHistogram(const Image& img);
}