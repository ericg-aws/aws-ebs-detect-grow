#!/usr/bin/env bash
# purpose: to package up python modules and app code for lambda 
# requirements: export AWS_REGION='us-east-1' && export FUNCTION_NAME='auto01-get-ebs-id' && export AWS_PROFILE='grmeri-training-admin'
# container: docker run -it --rm -v ${HOME}/repos/ebs-ec2-fs-grow/auto01-get-ebs-id/lambda:/ericg -v ${HOME}/.aws/credentials:/root/.aws/credentials:ro -e AWS_DEFAULT_PROFILE='grmeri-training-admin' -e AWS_REGION='us-east-1' -e FUNCTION_NAME='auto01-get-ebs-id' ericstephengarcia/codebuild-al2-3:latest bash

###### steps
# 1. read python requirements and download modules
# 2. zip up 
# 3. add python script 
# 4. update lambda function

# exit when a command fails 
set -e

MODULE_DIR='module'

rm -rf $MODULE_DIR
mkdir -p $MODULE_DIR

if [ -f requirements.txt ];then
    pip download -d ./$MODULE_DIR -r requirements.txt
    cd $MODULE_DIR

    # uncompress WHL files
    shopt -s nullglob
    file_list=(*.whl)
    for file in "${file_list[@]}"; do
          unzip $file
    done

    rm -rf *.whl *.dist-info __pycache__
    zip -r9 ../function.zip *
    cd ../
    rm -rf $MODULE_DIR
    zip -g function.zip lambda_function.py
    aws lambda update-function-code --region ${AWS_REGION} --function-name ${FUNCTION_NAME} --zip-file fileb://function.zip
    aws lambda update-function-configuration --region ${AWS_REGION} --function-name ${FUNCTION_NAME}
else
    echo "Missing requirements.txt file"
fi

