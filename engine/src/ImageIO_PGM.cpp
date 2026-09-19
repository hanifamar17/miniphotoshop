#include "ImageIO.Hpp"
#include <fstream>
#include <sstream>
#include <filesystem>
#include <iostream>
#include <new>
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

    //load citra PGM
    bool loadPGM(const string& filename, Image& img){
        ifstream fin(filename, ios::binary);
        if(!fin.is_open()){
            return false; //file tidak ketemu
        }

        //baca magic number
        string magic;
        fin >> magic;
        if(magic != "P2" && magic != "P5"){
            return false;
        }

        skipWhitespaceAndComments(fin);
        int width, height, maxval;
        fin >> width;
        skipWhitespaceAndComments(fin);
        fin >> height;
        skipWhitespaceAndComments(fin);
        fin >> maxval;
        fin.get(); //buang satu whitespace/newline setelah maxval

        if(width <= 0 || height <= 0 || maxval <= 0){
            return false;
        }

        try{
            img.allocate(width, height, 1); //PGM dengan ch=1
        }catch(const bad_alloc&){
            return false;
        }

        if(magic == "P5"){
            fin.read(reinterpret_cast<char*>(img.data.data()), img.data.size());
            if(!fin) return false;
        }else{
            for(size_t i = 0; i < img.data.size(); i++){
                int val;
                fin >> val;
                if(!fin) return false;
                img.data[i] = static_cast<uint8_t>(val);
            }
        }

        return true;
    }

    //save citra PGM
    bool savePGM(const string& filename, const Image& img, bool binary){
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
        fout<<(binary ? "P5" : "P2")<<"\n";
        fout<<img.width<<" "<<img.height<<"\n";
        fout<<255<<"\n"; //maxval (8-bit)

        if(binary){
            fout.write(reinterpret_cast<const char*>(img.data.data()), img.data.size());
        }else{
            for(size_t i = 0; i < img.data.size(); i++){
                fout<<static_cast<int>(img.data[i]);

                //newline tiap M (width)
                if((i + 1) % img.width == 0) fout<<"\n";
                else fout<<" ";
            }
        }

        return fout.good();
    }

    void printImageInfo(const string& filename, const Image& img){
        cout<<"Info Citra"<<endl;
        cout<<"Fil: "<<filename<<endl;
        cout<<"Lebar (M): "<<img.width<<endl;
        cout<<"Tinggi (N): "<<img.height<<endl;
        cout<<"Channels: "<<img.channels<<(img.channels == 1 ? " (Grayscale)" : " (Color)")<<endl;
        cout<<"Total px: "<<(img.width * img.height)<<endl;
        cout<<"Buffer: "<<img.data.size()<<" bytes (in-memory)"<<endl;

        //ukuran asli file di disk
        try{
            auto fileSize= filesystem::file_size(filename);
            cout<<"File size: "<<fileSize<<" bytes ("<<(fileSize/1024.0)<<" KB)"<<endl;
        }catch(const filesystem::filesystem_error& e){
            cout<<"File size: gagal baca (" <<e.what()<<")"<<endl;
        }
    }
}