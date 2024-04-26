#!./venv/bin/python
import subprocess
import boto3
import colorama
import json
import os

# the main diference is that we are going to create a bucket before running the terraform
# and we are going to use the bucket name in the vars.tfvars file to be used in the terraform
# we are going to use the same functions from the main.py file
# this creation of buckets will create a bucket without policy and wih a policy

s3 = boto3.client('s3')
sts = boto3.client('sts')
caller_identity = sts.get_caller_identity()
print(caller_identity['Account'])
writer_account_id = os.environ['WRITER_ACCOUNT_ID']
aimed_region = os.environ['REGION']
dir_path = '../../iac/reader/'

#1
def create_bucket():
  bucket_name = ["iac-dy-tester", "iac-dy-tester-policy"]
  bucket_policies = []

  for bname in bucket_name:
    policy = {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Sid": "AllowLisandroPintosReadWrite",
          "Effect": "Allow",
          "Principal": {
            "AWS": caller_identity['Account']
          },
          "Action": ["s3:GetObject", "s3:PutObject"],
          "Resource": f"arn:aws:s3:::{bname}/*"
        }
      ]
    }
    bucket_policies.append(json.dumps(policy))

  print(colorama.Fore.GREEN + f'Creating bucket {bucket_name}...' + colorama.Fore.RESET)
  s3.create_bucket(Bucket=bucket_name[0])
  s3.create_bucket(Bucket=bucket_name[1])
  s3.put_bucket_policy(Bucket=bucket_name[1], Policy=bucket_policies[1])
  print(colorama.Fore.GREEN + f'Bucket {bucket_name} created successfully...' + colorama.Fore.RESET)

  return bucket_name

def update_bucket_policy():
  for bname in ["iac-dy-tester", "iac-dy-tester-policy"]:
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
    print(colorama.Fore.GREEN + f'Updating bucket {bname} policy...' + colorama.Fore.RESET)
    old_policy = s3.get_bucket_policy(Bucket=bname)['Policy']
    old_policy_dict = json.loads(old_policy)
    old_policy_dict['Statement'] = [s for s in old_policy_dict['Statement'] if s['Sid'] != 'AllowS3ReaderRole']

    print(colorama.Fore.YELLOW + str(old_policy_dict["Statement"]) + colorama.Fore.RESET)
    for i in (old_policy_dict["Statement"]):
      policy['Statement'].append(i)
    bucket_policy = json.dumps(policy)
    print("\nNew policy:\n" + colorama.Fore.YELLOW + bucket_policy + colorama.Fore.RESET)
    print(colorama.Fore.GREEN + f'Updating bucket {bname} policy...' + colorama.Fore.RESET)
    s3.put_bucket_policy(Bucket=bname, Policy=bucket_policy)

#2
def terraform_build():
  with open(os.path.join(dir_path, '../reader-vars.tfvars'), 'w') as f:
    f.write(f'writer_account_id = "{writer_account_id}"\n')

  print(colorama.Fore.GREEN + 'Building Terraform...' + colorama.Fore.RESET)
  subprocess.run(['terraform', 'init'], cwd=dir_path, check=True)

  subprocess.run(['terraform plan -var-file ../reader-vars.tfvars -target module.shell'], cwd=dir_path, shell=True, check=True)
  print(colorama.Fore.GREEN + 'Apply Terraform...' + colorama.Fore.RESET)
  result = subprocess.run(['terraform apply -var-file ../reader-vars.tfvars -auto-approve -target module.shell | tail -n 20'], cwd=dir_path, shell=True, capture_output=True, check=True)
  output = result.stdout.decode()

  exit_code_lst = [int(i) for i in output.split() if i.isdigit()]
  if any(exit_code != 0 for exit_code in exit_code_lst):
    print(colorama.Fore.RED + 'Error Applying Terraform...' + colorama.Fore.RESET)
    print(colorama.Fore.RED + f'{output}' + colorama.Fore.RESET)
    exit(1)

  print(colorama.Fore.GREEN + 'No exit code error founded continuing with apply...' + colorama.Fore.RESET)
  result = subprocess.run(['terraform apply -var-file ../reader-vars.tfvars -auto-approve'], cwd=dir_path, shell=True, check=True)
  if result.returncode == 0:
    print(colorama.Fore.GREEN + 'Terraform Applied Successfully...' + colorama.Fore.RESET)

def main():
  colorama.init()
  create_bucket()
  update_bucket_policy()
 # terraform_build()
  colorama.deinit()

if __name__ == '__main__':
  main()