#!/bin/bash
sudo apt-get install git gawk m4 libpcre3-dev libwxgtk3.0-dev cmake g++ libgtkmm-3.0-dev uuid-dev libssl-dev sshfs gvfs-libs gvfs-backends gvfs-fuse libsecret-1-dev libssh-dev libsmbclient-dev libnfs-dev fakeroot libarchive-dev
sudo apt-get install libneon27-dev libuchardet-dev libchardet-dev libspdlog-dev libfmt-dev libxerces-c-dev

rm -rf far2l
git clone https://github.com/elfmz/far2l
cd far2l
mkdir build
cd build
cmake -DUSEWX=no -DPYTHON=yes -DCMAKE_BUILD_TYPE=Release ..
make -j4
# sudo make install
