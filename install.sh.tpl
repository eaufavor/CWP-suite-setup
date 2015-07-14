#!/bin/sh

installChrome=$installChrome
preInstall=$preInstall
installPackages=$installPackages
compileTshark=$compileTshark

if [ "$$preInstall" = true ]; then
    echo "pre-install"
    sudo apt-get install $$instalFirst
fi

if [ "$$installChrome" = true ]; then
    echo "adding google repo"
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    sudo sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
    sudo apt-get update
fi

if [ "$$installPackages" = true ]; then
    echo "Installing packages"
    sudo apt-get install $$toInstall
fi


echo "Installing chrome-har-capturer-cache"
sudo npm install -g ../chrome-har-capturer-cache

echo "Fixing tcpdump permission"
sudo setcap 'CAP_NET_RAW+eip CAP_NET_ADMIN+eip' /usr/sbin/tcpdump

echo "Creating chrome disk cache":
mkdir -p /tmp/tmpfs

echo "Installing pyshark-ssl";
sudo pip install ../pyshark-ssl/src

echo "Installing python-daemon"
sudo pip install python-daemon

if [ "$$compileTshark" = true ]; then
    echo "Downloading wireshark"
    cd ..
    wget $tsharkURL --no-check-certificate
    tar -xvf wireshark-1.99.7.tar.bz2
    cd wireshark-1.99.7
    echo "Patching wireshark"
    patch epan/proto.h < ../cwp-suite-setup/lable_limit.patch
    ./autogen.sh
    ./configure --disable-wireshark --with-ssl --with-gnutls
    make -j2
fi

echo 'Done'
