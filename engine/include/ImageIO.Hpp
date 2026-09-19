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

    //info
    void printImageInfo(const string& filename, const Image& img);
}
