#!/bin/bash

set -x 
if ! file lambda_package/cartogram | grep -q "GNU/Linux"; then
    echo "ERROR: lambda_package/cartogram is not a Linux executable."
    exit 1
fi

./package.sh || exit 1

aws lambda update-function-configuration \
    --function-name $LAMBDA_FUNCTION_NAME \
    --runtime python3.8 \
    || exit 1

aws lambda update-function-code \
    --function-name $LAMBDA_FUNCTION_NAME \
    --zip-file fileb://cartogram.zip > /dev/null 2>&1 \
    || exit 1

rm cartogram.zip

set +x
