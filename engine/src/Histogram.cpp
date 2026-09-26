#include "Histogram.hpp"
#include <cmath>

namespace mps{
    static void finalizeStats(HistogramData& h){
        h.totalPixels= 0;
        for(int i= 0; i <= 255; i++){
            h.totalPixels+= h.counts[i];
        }

        if(h.totalPixels == 0){
            return;
        }

        for(int i= 0; i <= 255; i++){
            h.normalized[i]= (double)h.counts[i] / (double)h.totalPixels;
        }

        for(int i= 0; i <= 255; i++){
            h.mean+= i * h.normalized[i];
        }

        for(int i= 0; i <= 255; i++){
            h.variance+= (i - h.mean) * (i - h.mean) * h.normalized[i];
        }

        h.stdv= sqrt(h.variance);
    }
    
    HistogramData computeHistogram(const Image& img){
        HistogramData h;
        if(img.empty()){
            return h;
        }

        for(int row= 0; row < img.height; row++){
            for(int col= 0; col < img.width; col++){
                h.counts[img.at(row, col, 0)]++;
            }
        }

        finalizeStats(h);
        return h;
    }

    ColorHistogramData computeColorHistogram(const Image& img){
        ColorHistogramData ch;
        if(img.empty() || img.channels != 3){
            return ch;
        }

        for(int row= 0; row < img.height; row++){
            for(int col= 0; col < img.width; col++){
                uint8_t r= img.at(row, col, 0);
                uint8_t g= img.at(row, col, 1);
                uint8_t b= img.at(row, col, 2);

                ch.red.counts[r]++;
                ch.green.counts[g]++;
                ch.blue.counts[b]++;

                int luminosity= (int)(0.299*r + 0.587*g + 0.114*b + 0.5);
                if(luminosity > 255){
                    luminosity= 255;
                }
                ch.luminosity.counts[luminosity]++;
            }

        }

        finalizeStats(ch.red);
        finalizeStats(ch.green);
        finalizeStats(ch.blue);
        finalizeStats(ch.luminosity);
        return ch;
    }
}