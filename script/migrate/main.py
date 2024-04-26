#!./venv/bin/python
import subprocess
import boto3
import colorama
import os

# use writer role

s3 = boto3.client('s3')
aws_account_id = os.environ['TARGET_ACCOUNT_ID']
destination_bucket = os.environ['DESTINATION_BUCKET']
print(colorama.Fore.GREEN + f'AWS Account ID: {aws_account_id}\n' + colorama.Fore.RESET
      + colorama.Fore.GREEN + f'Destination Bucket: {destination_bucket}\n' + colorama.Fore.RESET)

def current_s3_buckets():
  print(colorama.Fore.GREEN + 'Current S3 Buckets...')
  response = s3.list_buckets()
  for bucket in response['Buckets']:
    print(colorama.Fore.LIGHTBLUE_EX + f'{bucket["Name"]}' + colorama.Fore.RESET)
  return response['Buckets']

def sync_s3_bucket():
  source_buckets = current_s3_buckets()
  destination_bucket = os.environ['DESTINATION_BUCKET']
  print(colorama.Fore.GREEN + 'Syncing S3 Buckets...' + colorama.Fore.RESET)
  for bucket in source_buckets:
    source_bucket_name = bucket["Name"]
    print(colorama.Fore.LIGHTBLUE_EX + f'Syncing {source_bucket_name} to {destination_bucket}' + colorama.Fore.RESET)
    subprocess.run(['aws', 's3', 'sync', f's3://{source_bucket_name}', f's3://{destination_bucket}/{source_bucket_name}/'], check=True)
  print(colorama.Fore.GREEN + 'Synced S3 Buckets...' + colorama.Fore.RESET)


def main():
  colorama.init()
  sync_s3_bucket()
  colorama.deinit()

if __name__ == '__main__':
  main()