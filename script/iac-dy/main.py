#!./venv/bin/python
import subprocess
import boto3
import colorama
import json
import os

s3 = boto3.client('s3')
writer_account_id = os.environ['WRITER_ACCOUNT_ID']
caller_identity = boto3.client('sts').get_caller_identity()['Account']
aimed_region = os.environ['REGION']
dir_path = '../../iac/reader/'

#1
def current_s3_buckets():
    print(colorama.Fore.GREEN + 'Current S3 Buckets...' + colorama.Fore.RESET)
    response = s3.list_buckets()
    bucket_names = []
    for bucket in response['Buckets']:
        bucket_names.append(bucket['Name'])
    bucket_names_str = json.dumps(bucket_names)
    print(colorama.Fore.YELLOW + f'Bucket Names: {bucket_names_str}' + colorama.Fore.RESET)
    with open(os.path.join(dir_path, '../reader-vars.tfvars'), 'w') as f:
        f.write(f'writer_account_id = "{writer_account_id}"\n')
    return bucket_names_str

#2
def terraform_build():
  print(colorama.Fore.GREEN + 'Building Terraform...' + colorama.Fore.RESET)
  subprocess.run(['terraform', 'init'], cwd=dir_path, check=True)

  result = subprocess.run(['terraform plan -var-file ../reader-vars.tfvars -target module.shell'], cwd=dir_path, shell=True, check=True, capture_output=True)
  if result.returncode == 0:
    print(colorama.Fore.GREEN + 'Terraform Planned Successfully...' + colorama.Fore.RESET)
  else:
    print(colorama.Fore.RED + 'Terraform Plan Failed...' + colorama.Fore.RESET)
    print(colorama.Fore.RED + result.stderr.decode() + colorama.Fore.RESET)
    exit(1)

  result = subprocess.run(['terraform apply -var-file ../readers-vars.tfvars -auto-approve'], cwd=dir_path, shell=True, check=True, capture_output=True)
  if result.returncode == 0:
    print(colorama.Fore.GREEN + 'Terraform Applied Successfully...' + colorama.Fore.RESET)
  else:
    print(colorama.Fore.RED + 'Terraform Apply Failed...' + colorama.Fore.RESET)
    print(colorama.Fore.RED + result.stderr.decode() + colorama.Fore.RESET)
    exit(1)

def update_bucket_policy(buckets):
    for bname in buckets:
      policy = {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Sid": "AllowS3ReaderRole",
          "Effect": "Allow",
          "Principal": {
            "AWS": f"arn:aws:iam::{caller_identity}:role/S3ReaderRole"
          },
          "Action": [
              "s3:ListBucket",
              "s3:GetObject",
              "s3:PutObject",
              "s3:DeleteObject",
              "s3:ReplicateObject",
              "s3:ReplicateDelete"
          ],
          "Resource": [
            f"arn:aws:s3:::{bname}/*",
            f"arn:aws:s3:::{bname}"
          ]
        }
      ]
    }
      old_policy = s3.get_bucket_policy(Bucket=bname)['Policy']
      old_policy_dict = json.loads(old_policy)
      print(colorama.Fore.YELLOW + str(old_policy_dict["Statement"]) + colorama.Fore.RESET)
      for i in (old_policy_dict["Statement"]):
        policy['Statement'].append(i)
      bucket_policy = json.dumps(policy)
      print("\nNew policy:\n" + colorama.Fore.YELLOW + bucket_policy + colorama.Fore.RESET)
      print(colorama.Fore.GREEN + f'Updating bucket {bname} policy...' + colorama.Fore.RESET)
      s3.put_bucket_policy(Bucket=bname, Policy=bucket_policy)

def main():
  colorama.init()
  buckets = current_s3_buckets()
  terraform_build()
  update_bucket_policy(buckets=buckets)
  colorama.deinit()

if __name__ == '__main__':
  main()