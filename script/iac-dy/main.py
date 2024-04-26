#!./venv/bin/python
import subprocess
import boto3
import colorama
import os

s3 = boto3.client('s3')
writer_account_id = os.environ['WRITER_ACCOUNT_ID']
dir_path = '../../iac/reader/'

def current_s3_buckets():
  print(colorama.Fore.GREEN + 'Current S3 Buckets...' + colorama.Fore.RESET)
  response = s3.list_buckets()
  bucket_names = [bucket['Name'] for bucket in response['Buckets']]
  bucket_names_str = str(bucket_names).replace("'", '"')
  print(colorama.Fore.YELLOW + f'Bucket Names: {bucket_names_str}' + colorama.Fore.RESET)
  with open(os.path.join(dir_path, 'vars.tfvars'), 'w') as f:
    f.write(f'bucket_name = {bucket_names}\n')
    f.write(f'writer_account_id = "{writer_account_id}"\n')
  return bucket_names_str

def terraform_build():
  print(colorama.Fore.GREEN + 'Building Terraform...' + colorama.Fore.RESET)
  subprocess.run(['terraform', 'init'], cwd=dir_path, check=True)
  subprocess.run(['terraform', 'plan', '-var-file vars.tfvars', '-target module.shell'], cwd=dir_path, check=True)
  print(colorama.Fore.GREEN + 'Apply Terraform...' + colorama.Fore.RESET)
  os.sleep(5)
  error = open('error.log', 'w')
  subprocess.run(['terraform', 'apply', '-var-file vars.tfvars', '-auto-approve'], stderr=error, cwd=dir_path, check=True)
  if error:
    print(colorama.Fore.RED + 'Error Applying Terraform...' + colorama.Fore.RESET)
    exit(1)
  print(colorama.Fore.GREEN + 'Terraform Applied...' + colorama.Fore.RESET)

def main():
  colorama.init()
  current_s3_buckets()
  terraform_build()
  colorama.deinit()

if __name__ == '__main__':
  main()