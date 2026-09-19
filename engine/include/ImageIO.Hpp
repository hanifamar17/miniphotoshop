#pragma once
# include "Image.Hpp"

namespace mps{
    //PGM (Portable Gray Map) format
    bool loadPGM(const string& filename, Image& img);
    bool savePGM(const string& filename, const Image& img, bool binary= true);
    

    //PBM
    bool loadPBM(const string& filename, Image& img);
    bool savePBM(const string& filename, const Image& img, bool binary= true);


    //info
    void printImageInfo(const string& filename, const Image& img);
}
