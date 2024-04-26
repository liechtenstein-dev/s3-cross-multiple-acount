#! /bin/bash
# aws sts assume-role --role-arn arn:aws:iam::digital-latam-master-account-id:role/S3WriterRole --role-session-name S3CopySession

response=$(aws sts assume-role --role-arn arn:aws:iam::$1:role/$2 --role-session-name s3-access)
export AWS_ACCESS_KEY_ID=$(echo $response | jq -r .Credentials.AccessKeyId)
export AWS_SECRET_ACCESS_KEY=$(echo $response | jq -r .Credentials.SecretAccessKey)
export AWS_SESSION_TOKEN=$(echo $response | jq -r .Credentials.SessionToken)