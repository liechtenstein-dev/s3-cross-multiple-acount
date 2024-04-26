data "aws_caller_identity" "current" {}

module "shell" {
  count = length(var.bucket_name)
  source  = "Invicton-Labs/shell-resource/external"
  version = "0.4.1"
  command_unix = <<EOF
     aws s3api get-bucket-policy --bucket ${var.bucket_name[count.index]} 2&>/dev/null || echo "No policy"
  EOF
}

locals {
  stdout = module.shell[*].stdout
  count_bucket_policies = sum([for i in local.stdout: i != "No policy" ? 1 : 0])
}

resource "null_resource" "bucket" {
  count = local.count_bucket_policies
}

data "aws_s3_bucket_policy" "s3_existing_policy" {
  count  = local.count_bucket_policies
  bucket = var.bucket_name[count.index]
}

data "aws_iam_policy_document" "s3_reader_policy" {
  count = length(var.bucket_name)
  source_policy_documents = [
    data.aws_s3_bucket_policy.s3_existing_policy[count.index].policy == [] ? null : data.aws_s3_bucket_policy.s3_existing_policy[count.index].policy
  ]
  statement {
    sid       = "AllowS3ReaderRole"
    effect    = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/S3ReaderRole"]
    }
    actions = [
            "s3:ListBucket",
            "s3:GetObject",
            "s3:PutObject",
            "s3:DeleteObject",
            "s3:ReplicateObject",
            "s3:ReplicateDelete"
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