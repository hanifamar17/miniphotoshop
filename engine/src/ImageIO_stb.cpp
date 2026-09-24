#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"
#include "ImageIO.hpp"
#include <algorithm>
using namespace std;

namespace mps{
    //loader PNG/JPG
    static bool loadStb(const string& filename, Image& img){
        int w, h, c;
        if(!stbi_info(filename.c_str(), &w, &h, &c)){
            return false;
        }

        int want= (c <= 2) ? 1 : 3;
        unsigned char* d= stbi_load(filename.c_str(), &w, &h, &c, want);
        if(!d){
            return false;
        }

        img.allocate(w, h, want);
        copy(d, d + static_cast<size_t>(w) * h * want, img.data.begin());
        stbi_image_free(d);

        return true;
    }

    //load PNG
    bool loadPNG(const string& filename, Image& img){
        return loadStb(filename, img);
    }

    //savePNG
    bool savePNG(const string& filename, const Image& img){
        if(img.empty()){
            return false;
        }

        return stbi_write_png(filename.c_str(), img.width, img.height, img.channels, img.data.data(), img.width * img.channels) != 0;
    }

    //load JPG
    bool loadJPG(const string& filename, Image& img){
        return loadStb(filename, img);
    }

    //saveJPG
    bool saveJPG(const string& filename, const Image& img, int quality){
        if(img.empty()){
            return false;
        }

        return stbi_write_jpg(filename.c_str(), img.width, img.height, img.channels, img.data.data(), quality) != 0;
    }
}