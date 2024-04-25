#!./venv/bin/python
import subprocess
import boto3
import colorama
import os

s3 = boto3.client('s3')
#account_id = os.environ['ACCOUNT_ID']
#role_name = os.environ['ROLE_NAME']

def getting_caller_identity():
  print(colorama.Fore.GREEN + 'Current AWS Account...')
  subprocess.run(['aws', 'sts', 'get-caller-identity'], check=True)

def current_s3_buckets():
  print(colorama.Fore.GREEN + 'Current S3 Buckets...')
  response = s3.list_buckets()
  for bucket in response['Buckets']:
    print(colorama.Fore.LIGHTBLUE_EX + f'{bucket["Name"]}' + colorama.Fore.RESET)

def assume_role():
  print(colorama.Fore.GREEN + 'Assuming Role...' + colorama.Fore.RESET)
  subprocess.run(['aws', 'sts', 'assume-role', '--role-arn', f'arn:aws:iam::{account_id}:role/{role_name}', '--role-session-name', 'cross-s3-access',], check=True)

def main():
  colorama.init()

  getting_caller_identity()
  current_s3_buckets()
  assume_role()
  # copy s3 bucket cross account to another s3 bucket
  # aws_account_ids = ['123456789012', '123456789013']
  # for i in aws_account_ids:
  #   copy_s3_bucket(i)

  colorama.deinit()

if __name__ == '__main__':
  main()