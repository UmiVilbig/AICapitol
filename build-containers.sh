#!/bin/bash

# Navigate to ./monitor directory
cd ./monitor

# Build Docker image
docker build -t insider:1.0 .

# Navigate back to main
cd ..

# Navigate to ./bg_info directory
cd ./bg_info

# Build Docker image
docker build -t bg_info:1.0 .