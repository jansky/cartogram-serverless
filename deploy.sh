#!/bin/bash

set -x 
if ! file lambda_package/cartogram | grep -q "GNU/Linux"; then
    echo "ERROR: lambda_package/cartogram is not a Linux executable."
    exit 1
fi

./package.sh
aws lambda update-function-code --function-name $LAMBDA_FUNCTION_NAME --zip-file fileb://cartogram.zip || exit 1
rm cartogram.zip

set +x
