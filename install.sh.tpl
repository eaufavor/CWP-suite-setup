#!/bin/sh

installChrome=$installChrome
preInstall=$preInstall
installPackages=$installPackages
compileTshark=$compileTshark

if [ "$$preInstall" = true ]; then
    echo "pre-install"
    sudo apt-get --yes install $$instalFirst
fi

if [ "$$installChrome" = true ]; then
    echo "adding google repo"
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    sudo sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
    sudo apt-get update
fi

if [ "$$installPackages" = true ]; then
    echo "Installing packages"
    sudo apt-get --yes install $toInstall
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

echo "Installing iso8601"
sudo pip install iso8601

echo "Installing selenium"
sudo pip install selenium

if [ "$$compileTshark" = true ]; then
    echo "Downloading wireshark"
    cd ..
    wget -N $tsharkURL --no-check-certificate
    tar -xf wireshark-1.99.7.tar.bz2
    cd wireshark-1.99.7/epan
    echo "Patching wireshark"
    patch -N proto.h < ../../cwp-suite-setup/label_limit.patch
    cd ..
    ./autogen.sh
    ./configure --disable-wireshark --with-ssl --with-gnutls
    echo "compiling tshark"
    make -j4
fi

echo "Allowing TCP:8000"
sudo iptables -I INPUT -i eth0 -p tcp --dport 8000 -m state --state NEW,ESTABLISHED -j ACCEPT

echo 'Done'
