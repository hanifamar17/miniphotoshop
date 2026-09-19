#pragma once
# include "Image.Hpp"

namespace mps{
    // baca citra PGM
    bool loadPGM(const string& filename, Image& img);

    //save image PGM
    bool savePGM(const string& filename, const Image& img, bool binary= true);

    //info citra
    void printImageInfo(const string& filename, const Image& img);
}