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

echo "Done! You can check status with: systemctl status gpugov"
