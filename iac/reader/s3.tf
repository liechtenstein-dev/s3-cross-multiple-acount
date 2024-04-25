data "aws_caller_identity" "current" {}

data "aws_s3_bucket_policy" "s3_existing_policy" {
  count  = length(var.bucket_name)
  bucket = var.bucket_name[count.index]
}

data "aws_iam_policy_document" "s3_reader_policy" {
  count = length(var.bucket_name)
  source_policy_documents = [data.aws_s3_bucket_policy.s3_existing_policy[count.index].policy]
  statement {
    sid       = "AllowS3ReaderRole"
    effect    = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/S3ReaderRole"]
    }
    actions = [
      "s3:GetObject",
      "s3:ListBucket"
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