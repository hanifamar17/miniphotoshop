#include "ImageIO.Hpp"
#include <iostream>
using namespace std;
using namespace mps;

int main(int argc, char** argv){
    cout<<"start"<<endl; //debug 1
    if(argc < 2){
        cout<<"Usage: "<<argv[0]<<" <file.pgm>"<<endl;
        return 1;
    }

    string filename= argv[1];
    cout<<"filename: "<<filename<<endl; //debug 2
    Image img;

    cout<<"before loadPGM"<<endl; //debug 3
    bool ok = loadPGM(filename, img);
    cout<<"after loadPGM, ok="<<ok<<endl; //debug 4

    if(!ok){
        cout<<"Gagal load: "<<filename<<endl;
        return 1; 
    }

    printImageInfo(filename, img);

    //test save
    bool savedBinary= savePGM("output_binary.pgm", img, true);
    bool savedAscii= savePGM("output_ascii.pgm", img, false);
    cout<<"Save binary (P5): "<<(savedBinary ? "OK" : "GAGAL")<<endl;
    cout<<"Save ascii (P2): "<<(savedAscii ? "OK" : "GAGAL")<<endl;
    return 0;
}