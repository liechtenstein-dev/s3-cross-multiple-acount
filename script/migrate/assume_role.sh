#!/bin/sh
response=$(aws sts assume-role --role-arn arn:aws:iam::$TARGET_ACCOUNT_ID:role/S3ReaderRole --role-session-name s3-access)
echo $response | jq .
export AWS_ACCESS_KEY_ID=$(echo $response | jq -r .Credentials.AccessKeyId)
export AWS_SECRET_ACCESS_KEY=$(echo $response | jq -r .Credentials.SecretAccessKey)
export AWS_SESSION_TOKEN=$(echo $response | jq -r .Credentials.SessionToken)