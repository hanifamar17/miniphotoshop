#include "ImageIO.Hpp"
#include <fstream>
#include <new>
#include <iostream>
using namespace std;

namespace mps{

    //load citra
    bool loadRAW(const string& filename, Image& img){
        ifstream fin(filename, ios::binary);
        if(!fin.is_open()){
            return false; //file tidak ketemu
        }

        unsigned short int width, height;
        fin.read(reinterpret_cast<char*>(&width), sizeof(unsigned short int));
        fin.read(reinterpret_cast<char*>(&height), sizeof(unsigned short int));
        if(!fin) return false;

        if(width <= 0 || height <= 0){
            return false;
        }

        try{
            img.allocate(width, height, 1); //RAW IMAGE grayscale
        }catch(const bad_alloc&){
            return false;
        }

        fin.read(reinterpret_cast<char*>(img.data.data()), img.data.size());
        if(!fin) return false;

        return true;
    }

    //save citra
    bool saveRAW(const string& filename, const Image& img){
        if(img.empty()){
            return false;
        }
        if(img.channels != 1){
            return false; //hanya citra grayscale
        }

        ofstream fout(filename, ios::binary);
        if(!fout.is_open()){
            return false; //gagal buka file
        }

        unsigned short int width= static_cast<unsigned short int>(img.width);
        unsigned short int height= static_cast<unsigned short int>(img.height);

        fout.write(reinterpret_cast<const char*>(&width), sizeof(unsigned short int));
        fout.write(reinterpret_cast<const char*>(&height), sizeof(unsigned short int));
        fout.write(reinterpret_cast<const char*>(img.data.data()), img.data.size());

        return fout.good();
    }
}