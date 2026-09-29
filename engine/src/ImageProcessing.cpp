#include "ImageProcessing.hpp"
#include <cmath>

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

                double y = 0.299*r + 0.587*g + 0.144*b;

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
}