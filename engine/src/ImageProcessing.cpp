#include "ImageProcessing.hpp"
#include "Histogram.hpp"
#include <cmath>
#include <algorithm>
#include <random>

namespace mps{

    //Membuat citra negatif
    void makeNegative(Image& img){
        for(auto& v : img.data){
            v = 255 - v;
        }
    }

    //konversi RGB ke grayscale
    Image toGrayscale(const Image& img){
        Image result;

        if(img.channels != 3){
            return result;
        }

        try{
            result.allocate(img.width, img.height, 1);
        }catch(const bad_alloc&){
            return Image();
        }

        for(int row = 0; row < img.height; row++){
            for(int col = 0; col < img.width; col++){
                uint8_t r = img.at(row, col, 0);
                uint8_t g = img.at(row, col, 1);
                uint8_t b = img.at(row, col, 2);

                double y = 0.299*r + 0.587*g + 0.114*b;

                //clipping
                if(y < 0){
                    y = 0;
                }else if(y > 255){
                    y = 255;
                } 

                result.at(row, col) = static_cast<uint8_t>(y);
            }
        }
        return result;
    }

    //image brightening
    void brighten(Image& img, int b){
        for(auto& v : img.data){
            int temp= static_cast<int>(v) + b;

            //clipping
            if(temp < 0){
                v = 0;
            }else if(temp > 255){
                v = 255;
            }else{
                v = static_cast<uint8_t>(temp);
            }
        }
    }

    //clipping
    static uint8_t clampToByte(double v){
        if(v > 255.0){
            return 255;
        }else if(v < 0.0){
            return 0;
        }else{
            return(uint8_t)(v + 0.5);
        }
    }

    //transformasi nilai ke semua pixel
    static void applyLUT(Image& img, const uint8_t lut[256]){
        for(size_t i = 0; i < img.data.size(); i++){
            img.data[i] = lut[img.data[i]];
        }
    }

    //log transform
    void logTransform(Image& img){
        uint8_t lut[256];
        double c = 255.0/log(256.0);
        for(int r = 0; r < 256; r++){
            lut[r] = clampToByte(c * log(1.0 + r));
        }
        applyLUT(img, lut);
    }

    //inverse log
    void inverseLogTransform(Image& img){
        uint8_t lut[256];
        double c = 255.0/log(256.0);
        for(int r = 0; r < 256; r++){
            lut[r] = clampToByte(exp(r / c) - 1.0);
        }
        applyLUT(img, lut);
    }

    //transformasi pangkat
    void powerTransform(Image& img, double gamma, double c){
        uint8_t lut[256];
        for(int r = 0; r < 256; r++){
            lut[r] = clampToByte(255.0 * c * pow(r / 255.0, gamma));
        }
        applyLUT(img, lut);
    }

    //contrast stretching
    void contrastStretching(Image& img, int r1, int s1, int r2, int s2){
        uint8_t lut[256];
        for(int r = 0; r < 256; r++){
            double s;
            if(r < r1){
                s = (double)s1 * r/r1;
            }else if(r <= r2){
                if(r2 == r1){
                    s = s2;
                }else{
                    s = s1 + (double)(r - r1)*(s2 - s1)/(r2 - r1);
                }
            }else{
                    s = s2 + (double)(r - r2)*(255 - s2)/(255 - r2);
            }
            lut[r] = clampToByte(s);
        }
        applyLUT(img, lut);
    }

    //contrast stretching (otomatis)
    void autoContrastStretching(Image& img, double a, double b){
        long long hist[256] = {0};
        for(size_t i = 0; i < img.data.size(); i++){
            hist[img.data[i]]++;
        }
        double total = (double)img.data.size();
        double lowLimit = total * a / 100.0;
        double highLimit = total * (100.0 - b) / 100.0;

        int rmin = 0;
        long long cum = 0;
        for(int r = 0; r < 256; r++){
            cum += hist[r];
            if(cum > lowLimit){
                rmin = r;
                break;
            }
        }

        int rmax = 255;
        cum = 0;
        for(int r = 255; r >= 0; r--){
            cum += hist[r];
            if(cum > highLimit){
                rmax = r;
                break;
            }
        }

        if(rmin >= rmax){
            return;
        }

        uint8_t lut[256];
        for(int r = 0; r < 256; r++){
            lut[r] = clampToByte(255.0 * (r - rmin) / (rmax - rmin));
        }
        applyLUT(img, lut);
    }
    
    //gray-level slicing
    void graySlicing(Image& img, int a, int b, bool preserveBackground, int highlight, int background){
        if(a > b){
            int t = a;
            a = b;
            b = t;
        }

        uint8_t lut[256];
        for(int r = 0; r < 256; r++){
            if(r >= a && r <= b){
                lut[r] = clampToByte(highlight);
            }else if(preserveBackground){
                lut[r] = (uint8_t)r;
            }else{
                lut[r] = clampToByte(background);
            }
        }
        applyLUT(img, lut);
    }

    //bit-plane slicing
    void bitPlaneSlicing(Image& img, int k, bool binary){
        if(k < 0 || k > 7){
            return;
        }

        uint8_t lut[256];
        for(int r = 0; r < 256; r++){
            int bit = (r >> k) & 1;
            if(binary){
                lut[r] = bit ? 255 : 0;
            }else{
                lut[r] = (uint8_t)(bit << k);
            }
        }
        applyLUT(img, lut);
    }

    //perataan histogram (equalization)
    void equalizeHistogram(Image& img){
        if(img.empty()){
            return;
        }

        const int L = 256;
        const int C = img.channels;
        const size_t npix = (size_t)img.width * img.height;

        HistogramData hist[3];
        if(C == 1){
            hist[0] = computeHistogram(img);
        }else if(C == 3){
            ColorHistogramData ch = computeColorHistogram(img);
            hist[0] = ch.red;
            hist[1] = ch.green;
            hist[2] = ch.blue;
        }else{
            return;
        }

        for(int c = 0; c < C; c++){
            bool flat = false;
            for(int k = 0; k < L; k++){
                if((size_t)hist[c].counts[k] == npix){
                    flat = true;
                    break;
                }
            }

            if(flat){
                continue;
            }

            uint8_t lut[L];
            size_t cum = 0;
            for(int k = 0; k < L; k++){
                cum += (size_t)hist[c].counts[k];
                lut[k] = (uint8_t)((double)cum / npix * (L - 1) + 0.5);
            }

            for(size_t i = 0; i < npix; i++){
                img.data[i*C + c] = lut[img.data[i*C + c]];
            }
        }
    }

    //konvolusi 1 channel
    static vector<double> convolveChannel(const Image& img, int c, const vector<double>& kernel, int ksize){
        const int r = ksize/2;
        vector<double> out((size_t)img.width * img.height);

        for(int row = 0; row < img.height; row++){
            for(int col = 0; col < img.width; col++){
                double sum = 0;
                for(int u = -r; u <= r; u++){
                    int rr = min(max(row + u, 0), img.height - 1);
                    for(int v = -r; v <= r; v++){
                        int cc = min(max(col + v, 0), img.width - 1);
                        sum += kernel[(u + r) * ksize + (v + r)] * img.at(rr, cc, c);
                    }
                }
                out[(size_t)row * img.width + col] = sum;
            }
        }
        return out;
    }

    //gaussian kernel
    static vector<double> makeGaussianKernel(int ksize, double sigma){
        const int r = ksize / 2;
        vector<double> kernel((size_t)ksize * ksize);
        double sum = 0;

        for(int u = -r; u <= r; u++){
            for(int v = -r; v <= r; v++){
                double val = exp(-(u * u + v * v) / (2.0 * sigma * sigma));
                kernel[(u + r) * ksize + (v + r)] = val;
                sum += val;
            }
        }
        for(size_t i = 0; i < kernel.size(); i++){
                kernel[i] /= sum;
        }
        return kernel;
    }

    static void applyKernel(Image& img, const vector<double>& kernel, int ksize){
        for(int c = 0; c < img.channels; c++){
            vector<double> out = convolveChannel(img, c, kernel, ksize);
            for(size_t i = 0; i < out.size(); i++){
                img.data[i * img.channels + c] = clampToByte(out[i]);
            }               
        }
    }

    //smoothing: mean filter
    void meanFilter(Image& img, int ksize){
        if(img.empty() || ksize < 3 || ksize % 2 == 0){
            return;
        }

        vector<double> kernel(ksize * ksize, 1.0 / (ksize * ksize));

        applyKernel(img, kernel, ksize);
    }

    //smoothing: gaussian filter
    void gaussianFilter(Image& img, int ksize, double sigma){
        if(img.empty() || ksize < 3 || ksize % 2 == 0 || sigma <= 0.0){
            return;
        }
        applyKernel(img, makeGaussianKernel(ksize, sigma), ksize);
    }

    //smoothing: median filter
    void medianFilter(Image& img, int ksize){
        if(img.empty() || ksize < 3 || ksize % 2 == 0){
            return;
        }

        const int r = ksize / 2;
        const Image src = img;
        vector<uint8_t> window(ksize * ksize);
        
        for(int c = 0; c < img.channels; c++){
            for(int row = r; row < img.height - r; row++){
                for(int col = r; col < img.width - r; col++){
                    size_t k = 0;

                    for(int u = -r; u <= r; u++){
                        for(int v = -r; v <= r; v++){
                            window[k++] = src.at(row + u, col + v, c);
                        }
                    }
                    nth_element(window.begin(), window.begin() + window.size() / 2, window.end());
                    img.at(row, col, c) = window[window.size() / 2];
                }
            }
        }
    }

    //edge detection: sobel
    //mode 0: |Gx|+|Gy|, 1: max(|Gx|,|Gy|), 2: sqrt(Gx^2+Gy^2), 3: (|Gx|+|Gy|)/2
    void sobelFilter(Image& img, int mode){
        if(img.empty() || mode < 0 || mode > 3){
            return;
        }

        const vector<double> sx = {
            -1, 0, 1,
            -2, 0, 2,
            -1, 0, 1
        };
        const vector<double> sy = {
            1, 2, 1,
            0, 0, 0,
            -1, -2, -1
        };

        for(int c = 0; c < img.channels; c++){
            vector<double> gx = convolveChannel(img, c, sx, 3);
            vector<double> gy = convolveChannel(img, c, sy, 3);
            for(int row = 0; row < img.height; row++){
                for(int col = 0; col < img.width; col++){
                    size_t i = (size_t)row * img.width + col;
                    double v;
                    if(row < 1 || row >= img.height - 1 || col < 1 || col >= img.width - 1){
                        v = 0.0;
                    }else{
                        double a = fabs(gx[i]);
                        double b = fabs(gy[i]);
                        if(mode == 0){
                            v = a + b;
                        }else if(mode == 1){
                            v = max(a, b);
                        }else if(mode == 2){
                            v = sqrt(a * a + b * b);
                        }else{
                            v = (a + b) / 2.0;
                        }
                    }
                    img.data[i * img.channels + c] = clampToByte(v);
                }
            }
        }
    }

    //noise: salt & pepper
    void addSaltPepper(Image& img, double prob, unsigned int seed){
        if(img.empty() || prob <= 0.0){
            return;
        }
        if(prob > 1.0){
            prob = 1.0;
        }

        mt19937 rng(seed);
        uniform_real_distribution<double> dist(0.0, 1.0);

        for(int row = 0; row < img.height; row++){
            for(int col = 0; col < img.width; col++){
                double p = dist(rng);
                if(p < prob){
                    uint8_t val = (p < prob / 2.0) ? 0 : 255;
                    for(int c = 0; c < img.channels; c++){
                        img.at(row, col, c) = val;
                    }
                }
            }
        }
    }
}