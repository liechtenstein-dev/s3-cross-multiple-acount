data "aws_caller_identity" "current" {}

module "shell" {
  count = length(var.bucket_name)
  source  = "Invicton-Labs/shell-resource/external"
  version = "0.4.1"
  command_unix = "aws s3api get-bucket-policy --bucket ${var.bucket_name[count.index]} 2&>/dev/null || echo $?"
}

locals {
  exit_code_lst = module.shell[*].exit_code
  count_bucket_policies = sum([for i in local.exit_code_lst: i  != 0 ? 1 : 0])
}

resource "null_resource" "bucket" {
  count = local.count_bucket_policies == 0 ? 0 : length(var.bucket_name)
}

data "aws_s3_bucket_policy" "s3_existing_policy" {
  count  = local.count_bucket_policies == 0 ? 0 : length(var.bucket_name)
  bucket = var.bucket_name[count.index]
}

locals {
  bucket_policy = try([jsondecode(data.aws_s3_bucket_policy.s3_existing_policy[*].policy)], [""])
}

data "aws_iam_policy_document" "s3_reader_policy" {
  count = length(var.bucket_name)
  source_policy_documents = local.bucket_policy == [""] ? [local.bucket_policy[0]] : [local.bucket_policy[count.index]]
  statement {
    sid       = "AllowS3ReaderRole"
    effect    = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/S3ReaderRole"]
    }
    actions = [
      "s3:GetObject",
      "s3:ListBucket",
    ]
    resources = [
      "arn:aws:s3:::${var.bucket_name[count.index]}",
      "arn:aws:s3:::${var.bucket_name[count.index]}/*"
    ]
  }
}

resource "aws_s3_bucket_policy" "s3_updated_policy" {
  count  = length(var.bucket_name)
  bucket = var.bucket_name[count.index]
  policy = data.aws_iam_policy_document.s3_reader_policy[count.index].json
}