#!/usr/bin/env bash
cp -r * ../build/
cd ../build
pip3 install -r requirements.txt -t .