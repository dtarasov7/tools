#!/bin/bash
set -e

sudo dnf -y install epel-release
sudo dnf -y install gawk m4 glib2-devel wxGTK3-devel cmake gcc-c++ git


sudo dnf -y install dnf-plugins-core
sudo dnf -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm
sudo dnf config-manager --set-enabled PowerTools


sudo dnf -y install libssh-devel
sudo dnf -y install libsmbclient-devel
sudo dnf -y install libnfs-devel
sudo dnf -y install libarchive-devel
sudo dnf -y install python3-devel
sudo dnf -y install virtualenv
sudo dnf -y install openssl-devel
sudo dnf -y install neon-devel

rm -rf ./far2l
git clone https://github.com/elfmz/far2l
cd ./far2l
mkdir ./build
cd ./build
cmake3 -DUSEWX=no -DPYTHON=yes -DCMAKE_BUILD_TYPE=Release ..
make -j4
sudo make install
cd ../..
rm -rf ./far2l
