#include "ImageIO.Hpp"
#include <fstream>
#include <new>
#include <iostream>
#include <cstdint>
#include <algorithm>
using namespace std;

namespace mps{

    #pragma pack(push, 1)
    struct BMPFileHeader{
        uint16_t bmpType; //BM=0x4D42
        uint32_t bmpSize;
        uint16_t reserved1;
        uint16_t reserved2;
        uint32_t offBits;
    };

    struct BMPInfoHeader{
        uint32_t hdrSize;
        int32_t width;
        int32_t height;
        uint16_t planes;
        uint16_t bitCount;
        uint32_t compression;
        uint32_t imgSize;
        int32_t horzRes;
        int32_t vertRes;
        uint32_t clrUsed;
        uint32_t clrImportant;
    };
    #pragma pack(pop)

    //load citra
    bool loadBMP(const string& filename, Image& img){
        ifstream fin(filename, ios::binary);
        if(!fin.is_open()){
            return false; //file tidak ketemu
        }

        BMPFileHeader fileHdr;
        fin.read(reinterpret_cast<char*>(&fileHdr), sizeof(BMPFileHeader));
        if(!fin) return false;

        if(fileHdr.bmpType != 0x4D42){
            return false; //bukan file BMP
        }

        BMPInfoHeader infoHdr;
        fin.read(reinterpret_cast<char*>(&infoHdr), sizeof(BMPInfoHeader));
        if(!fin) return false;

        if(infoHdr.compression != 0){
            return false; //hanya BMP tanpa kompresi
        }

        int width= infoHdr.width;
        int height= infoHdr.height;
        bool flipped= height > 0; //jika height>0, bottom-up
        if(height < 0) height= -height; //top-down

        if(width <= 0 || height <= 0){
            return false;
        }

        int bitCount= infoHdr.bitCount;
        if(bitCount != 1 && bitCount != 8 && bitCount != 24 && bitCount != 32){
            return false; //hanya BMP 1-bit (biner), 8-bit (gray) dan 24-bit (RGB)
        }

        int channels= (bitCount == 24 || bitCount == 32) ? 3 : 1;

        try{
            img.allocate(width, height, channels);
        }catch(const bad_alloc&){
            return false;
        }

        //skip ke data pixel
        fin.seekg(fileHdr.offBits, ios::beg);
        if(!fin) return false;

        int bytesPerPixelRow = (bitCount == 1) ? ((width + 7) / 8) : (width * (bitCount / 8));
        int rowSize= (bytesPerPixelRow + 3) & ~3;
        vector<uint8_t> rowBuffer(rowSize);

        for(int r=0; r < height; r++){
            fin.read(reinterpret_cast<char*>(rowBuffer.data()), rowSize);
            if(!fin) return false;

            int destRow= flipped ? (height - 1 - r) : r; //jika bottom-up, simpan di baris terbalik

            if(bitCount == 32){
                for(int col = 0; col < width; col++){
                    uint8_t b= rowBuffer[col * 4 + 0];
                    uint8_t g= rowBuffer[col * 4 + 1];
                    uint8_t rr= rowBuffer[col * 4 + 2];
                    // byte ke-4 alpha, diabaikan
                    img.at(destRow, col, 0)= rr;
                    img.at(destRow, col, 1)= g;
                    img.at(destRow, col, 2)= b;
                }
            }if(bitCount == 24){
                for(int col = 0; col < width; col++){
                    // BMP 24-bit: BGR
                    uint8_t b= rowBuffer[col * 3 + 0];
                    uint8_t g= rowBuffer[col * 3 + 1];
                    uint8_t rr= rowBuffer[col * 3 + 2];
                    img.at(destRow, col, 0)= rr;
                    img.at(destRow, col, 1)= g;
                    img.at(destRow, col, 2)= b;
                }
            }else if (bitCount == 8){
                // BMP 8-bit: grayscale
                for(int col = 0; col < width; col++){
                    img.at(destRow, col)= rowBuffer[col];
                }
            }else{
                // BMP 1-bit: biner
                for (int col = 0; col < width; col++) {
                    int byteIdx = col / 8;
                    int bitIdx = 7 - (col % 8);
                    int pixelVal = (rowBuffer[byteIdx] >> bitIdx) & 1;
                    img.at(destRow, col) = static_cast<uint8_t>(pixelVal ? 255 : 0);
                }
            }
        }

        return true;
    }

    //save citra
    bool saveBMP(const string& filename, const Image& img){
        if(img.empty()){
            return false;
        }
        if(img.channels != 1 && img.channels != 3){
            return false; //hanya citra grayscale dan RGB
        }

        ofstream fout(filename, ios::binary);
        if(!fout.is_open()){
            return false; //gagal buka file
        }

        // deteksi biner: semua nilai cuma 0 atau 255 (dan channels == 1)
        bool isBinary = false;
        if (img.channels == 1) {
            isBinary = true;
            for (uint8_t v : img.data) {
                if (v != 0 && v != 255) {
                    isBinary = false;
                    break;
                }
            }
        }

        int bitCount= (img.channels == 3) ? 24 : (isBinary ? 1 : 8);
        int bytesPerPixelRow = (bitCount == 1) ? ((img.width + 7) / 8) : (img.width * (bitCount / 8));
        int rowSize= (bytesPerPixelRow + 3) & ~3;

        int paletteSize= 0;
        if(bitCount == 1) paletteSize = 2 * 4;
        else if (bitCount == 8) paletteSize = 256 * 4;

        int dataSize= rowSize * img.height;

        BMPFileHeader fileHdr;
        fileHdr.bmpType= 0x4D42;
        fileHdr.offBits= sizeof(BMPFileHeader) + sizeof(BMPInfoHeader) + paletteSize;
        fileHdr.bmpSize= fileHdr.offBits + dataSize;
        fileHdr.reserved1= 0;
        fileHdr.reserved2= 0;

        BMPInfoHeader infoHdr{};
        infoHdr.hdrSize= sizeof(BMPInfoHeader);
        infoHdr.width= img.width;
        infoHdr.height= img.height; //positif = bottom-up
        infoHdr.planes= 1;
        infoHdr.bitCount= static_cast<uint16_t>(bitCount);
        infoHdr.compression= 0;
        infoHdr.imgSize= dataSize;
        infoHdr.horzRes= 2835; //~72 DPI
        infoHdr.vertRes= 2835;
        infoHdr.clrUsed= (bitCount == 1) ? 2 : (bitCount == 8 ? 256 : 0);
        infoHdr.clrImportant= 0;

        fout.write(reinterpret_cast<const char*>(&fileHdr), sizeof(fileHdr));
        fout.write(reinterpret_cast<const char*>(&infoHdr), sizeof(infoHdr));

        if (bitCount == 1) {
            // palette: entry 0 = hitam, entry 1 = putih
            uint8_t black[4] = {0, 0, 0, 0};
            uint8_t white[4] = {255, 255, 255, 0};
            fout.write(reinterpret_cast<const char*>(black), 4);
            fout.write(reinterpret_cast<const char*>(white), 4);
        }else if(bitCount == 8){
            //buat palet grayscale
            for(int i=0; i < 256; i++){
                uint8_t entry[4] = {
                    static_cast<uint8_t>(i), static_cast<uint8_t>(i),
                    static_cast<uint8_t>(i), 0
                };
                fout.write(reinterpret_cast<const char*>(entry), 4);
            }
        }
        
        vector<uint8_t> rowBuffer(rowSize, 0);

        //BMP disimpan bottom-up, bari citra citra ditulis dulu
        for(int r = img.height - 1; r >= 0; r--){
            fill(rowBuffer.begin(), rowBuffer.end(), 0);
            
            if(bitCount == 24){
                for(int col = 0; col < img.width; col++){
                    rowBuffer[col * 3 + 0]= img.at(r, col, 2); //b
                    rowBuffer[col * 3 + 1]= img.at(r, col, 1); //g
                    rowBuffer[col * 3 + 2]= img.at(r, col, 0); //r
                }
            }else if(bitCount == 8){
                for(int col = 0; col < img.width; col++){
                    rowBuffer[col]= img.at(r, col);
                }
            }else{
                for (int col = 0; col < img.width; col++) {
                    int pixelVal = (img.at(r, col) != 0) ? 1 : 0;
                    int byteIdx = col / 8;
                    int bitIdx = 7 - (col % 8);
                    if (pixelVal) {
                        rowBuffer[byteIdx] |= (1 << bitIdx);
                    }
                }
            }
            fout.write(reinterpret_cast<const char*>(rowBuffer.data()), rowSize);
        }

        return fout.good();
    }
}