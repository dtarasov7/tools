#!/bin/bash
set -e

rm -rf ./far2l
git clone https://github.com/elfmz/far2l
cd ./far2l
mkdir ./build
cd ./build
cmake -DUSEWX=no -DPYTHON=yes -DCMAKE_BUILD_TYPE=Release ..
make -j4
#sudo make install
#cd ../..
#rm -rf ./far2l
