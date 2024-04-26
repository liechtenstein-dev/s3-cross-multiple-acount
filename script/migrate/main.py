#!./venv/bin/python
import subprocess
import boto3
import colorama
import os

# use writer role

s3 = boto3.client('s3')
account_id = boto3.client('sts').get_caller_identity().get('Account')
role_name = os.environ['ROLE_NAME']
destination_bucket = os.environ['DESTINATION_BUCKET']

def current_s3_buckets():
  print(colorama.Fore.GREEN + 'Current S3 Buckets...')
  response = s3.list_buckets()
  for bucket in response['Buckets']:
    print(colorama.Fore.LIGHTBLUE_EX + f'{bucket["Name"]}' + colorama.Fore.RESET)
  return response['Buckets']

def assume_role():
  print(colorama.Fore.GREEN + 'Assuming Role...' + colorama.Fore.RESET)
  subprocess.run([f"bash ./assume_role.sh {account_id} {role_name}"], shell=True)
  if os.environ.get('AWS_ACCESS_KEY_ID') is None:
    print(colorama.Fore.RED + 'Role not assumed...' + colorama.Fore.RESET)
    exit(1)
  print(colorama.Fore.GREEN + 'Role assumed...' + colorama.Fore.RESET)

def sync_s3_bucket():
  source_bucket = current_s3_buckets()
  destination_bucket = os.environ['DESTINATION_BUCKET']
  print(colorama.Fore.GREEN + 'Syncing S3 Buckets...' + colorama.Fore.RESET)
  for bucket in source_bucket:
    print(colorama.Fore.LIGHTBLUE_EX + f'Syncing {bucket["Name"]} to {destination_bucket}' + colorama.Fore.RESET)
    subprocess.run(['aws', 's3', 'sync', f's3://{source_bucket}', f's3://{destination_bucket}/{source_bucket}/', '--acl', 'bucket-owner-full-control'], check=True)
  print(colorama.Fore.GREEN + 'Synced S3 Buckets...' + colorama.Fore.RESET)


def main():
  colorama.init()

  assume_role()
  sync_s3_bucket()

  colorama.deinit()

if __name__ == '__main__':
  main()