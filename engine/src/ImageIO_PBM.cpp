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
    bool loadPBM(const string& filename, Image& img){
        ifstream fin(filename, ios::binary);
        if(!fin.is_open()){
            return false; //file tidak ketemu
        }

        //baca magic number (P1/P4)
        string magic;
        fin >> magic;
        if(magic != "P1" && magic != "P4"){
            return false;
        }

        skipWhitespaceAndComments(fin);
        int width, height;
        fin >> width;
        skipWhitespaceAndComments(fin);
        fin >> height;
        fin.get(); //buang satu whitespace setelah height

        if(width <= 0 || height <= 0){
            return false;
        }

        try{
            img.allocate(width, height, 1); //PGM dengan ch=1
        }catch(const bad_alloc&){
            return false;
        }

        if(magic == "P1"){
            // ASCII: baca angka 0/1 satu-satu, pisah pakai spasi/newline
            for(size_t i = 0; i < img.data.size(); i++){
                int val;
                fin>>val;
                if(!fin) return false;
                img.data[i]= static_cast<uint8_t>(val);
            }
        }else{
            // binary: baca byte-byte, tiap bit mewakili satu pixel
            int bytesPerRow= (width + 7) / 8; //jumlah byte per baris
            for(int row = 0; row < height; row++){
                for(int byteIdx = 0; byteIdx < bytesPerRow; byteIdx++){
                    char byteVal;
                    fin.get(byteVal);
                    if(!fin) return false;

                    unsigned char b= static_cast<unsigned char>(byteVal);
                    for(int bit = 0; bit < 8; bit++){
                        int col= byteIdx * 8 + bit;
                        if(col >= width) break;

                        int pixelVal= (b >> (7 - bit)) & 1;
                        img.at(row, col)= static_cast<uint8_t>(pixelVal);
                    }
                }
            }
        }

        return true;
    }

    //save citra
    bool savePBM(const string& filename, const Image& img, bool binary){
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

        //header
        fout<<(binary ? "P1" : "P4")<<"\n";
        fout<<img.width<<" "<<img.height<<"\n";

        if(binary){
            int bytesPerRow= (img.width + 7)/8;
            for(int row = 0; img.height; row++){
                for(int byteIdx = 0; byteIdx < bytesPerRow; byteIdx++){
                    unsigned char b = 0;
                    for(int bit = 0; bit < 8; bit++){
                        int col = byteIdx * 8 + bit;
                        if(col >= img.width) break;
                        int pixelVal = img.at(row, col) ? 1 : 0;
                        b |= (pixelVal << (7 - bit));
                    }
                    fout.put(static_cast<char>(b));
                }
            }
        }else{
            for(int row= 0; row < img.height; row++){
                for(int col= 0; col < img.width; col++){
                    fout<<(img.at(row, col) ? 1 : 0);
                    fout<<(col == img.width - 1 ? "" : " ");
                }
                fout<<"\n";
            }
        }
        return fout.good();
    }
}