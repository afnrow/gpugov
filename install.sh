#!/bin/bash

if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root (sudo ./install.sh)"
  exit 1
fi

echo "--- GPUGOV  ---"

echo "Compiling..."
make clean
make all

if [ $? -eq 0 ]; then
    echo "Compilation successful."
else
    echo "Compilation failed. Check for missing clang or headers."
    exit 1
fi

echo "Installing files..."
make install

systemctl enable gpugov.service
systemctl start gpugov.service

sudo touch /etc/gpugov.conf
if [ ! -f /etc/gpugov.conf ]; then
    echo -e "temp_critical=85.0\nbat_critical=20" > /etc/gpugov.conf
fi
chmod 644 /etc/gpugov.conf
