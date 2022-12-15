#!/bin/bash

set -x
rm -f cartogram.zip

rm -rf ./package
pip install --target ./package -r requirements.txt || exit 1

cd package
zip -r9 ../cartogram.zip . || exit 1

cd ../lambda_package
zip -g ../cartogram.zip cartogram cartogram_c *.py || exit 1

cd ../
rm -rf ./package

set +x
