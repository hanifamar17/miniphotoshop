#include "ImageProcessing.hpp"

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
}