#pragma once
#include <vector>
#include <cstdint>
#include <string>
using namespace std;

namespace mps{

    //struktur data utama citra
    struct Image{
        int width= 0;
        int height= 0;
        int channels= 0; //1 u/grayscale, 3 u/rgb
        vector<uint8_t> data;

        bool empty() const{
            return data.empty() || width <= 0 || height <= 0;
        }

        uint8_t& at(int row, int col, int c= 0){
            return data[(row * width + col) * channels + c];
        }

        const uint8_t& at(int row, int col, int c= 0) const{
            return data[(row * width + col) * channels + c];
        }

        void allocate(int w, int h, int ch){
            width= w;
            height= h;
            channels= ch;
            data.assign(static_cast<size_t>(w) * h * ch, 0);
        }
    };
}