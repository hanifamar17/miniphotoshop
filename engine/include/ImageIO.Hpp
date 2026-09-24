#pragma once
# include "Image.Hpp"

namespace mps{
    //PGM (Portable Graymap) format
    bool loadPGM(const string& filename, Image& img);
    bool savePGM(const string& filename, const Image& img, bool binary= true);
    
    //PPM (Portable Pixelmap) format
    bool loadPPM(const string& filename, Image& img);
    bool savePPM(const string& filename, const Image& img, bool binary= true);

    //PBM (Portable Bitmap) format
    bool loadPBM(const string& filename, Image& img);
    bool savePBM(const string& filename, const Image& img, bool binary= true);

    //RAW IMAGE
    bool loadRAW(const string& filename, Image& img);
    bool saveRAW(const string& filename, const Image& img);

    //BMP
    bool loadBMP(const string& filename, Image& img);
    bool saveBMP(const string& filename, const Image& img);

    //PNG
    bool loadPNG(const string& filename, Image& img);
    bool savePNG(const string& filename, const Image& img);

    //JPG
    bool loadJPG(const string& filename, Image& img);
    bool saveJPG(const string& filename, const Image& img, int quality=90);

    //info
    void printImageInfo(const string& filename, const Image& img);
}
