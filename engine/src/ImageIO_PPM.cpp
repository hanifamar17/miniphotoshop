#include "ImageIO.Hpp"
#include <fstream>
#include <new>
#include <iostream>
using namespace std;

namespace mps{

    static void skipWhitespaceAndComments(ifstream& fin){
        char c;
        while(fin.get(c)){
            if(c == '#'){
                string dummy; //skip s.d akhir baris
                getline(fin, dummy);
            }else if(!isspace(static_cast<unsigned char>(c))){
                fin.unget();
                break;
            }
        }
    }

    //load citra
    bool loadPPM(const string& filename, Image& img){
        ifstream fin(filename, ios::binary);
        if(!fin.is_open()){
            return false; //file tidak ketemu
        }

        //baca magic number (P3/P6)
        string magic;
        fin >> magic;
        if(magic != "P3" && magic != "P6"){
            return false;
        }

        skipWhitespaceAndComments(fin);
        int width, height, maxval;
        fin >> width;
        skipWhitespaceAndComments(fin);
        fin >> height;
        skipWhitespaceAndComments(fin);
        fin >> maxval;
        skipWhitespaceAndComments(fin); //handle komentar setelah maxval

        if(maxval <= 0 || maxval > 255){
            return false; //hanya support 8-bit per channel
        }

        try{
            img.allocate(width, height, 3); //PPM dengan ch=3 (rgb)
        }catch(const bad_alloc&){
            return false;
        }

        if(magic == "P6"){
            // binary: baca byte-byte
            fin.read(reinterpret_cast<char*>(img.data.data()), img.data.size());
            if(!fin) return false;
        }else{
            // ASCII: baca angka-angka 0..255 satu-satu
            for(size_t i = 0; i < img.data.size(); i++){
                int val;
                fin>>val;
                if(!fin) return false;
                img.data[i] = static_cast<uint8_t>(val);
            }
        }

        return true;
    }

    //save citra
    bool savePPM(const string& filename, const Image& img, bool binary){
        if(img.empty()){
            return false;
        }
        if(img.channels != 3){
            return false; //hanya citra RGB
        }

        ofstream fout(filename, ios::binary);
        if(!fout.is_open()){
            return false; //gagal buka file
        }

        //header
        fout<<(binary ? "P6" : "P3")<<"\n";
        fout<<img.width<<" "<<img.height<<"\n";
        fout<<255 << "\n"; //maxval

        if(binary){
            fout.write(reinterpret_cast<const char*>(img.data.data()), img.data.size());
        }else{
            for(size_t i= 0; i < img.data.size(); i++){
                fout<<static_cast<int>(img.data[i]);
                //newline tiap pixel (3 channel)
                if((i + 1) % 3 == 0) fout<<"\n";
                else fout<<" ";
            }
        }
        return fout.good();
    }
}