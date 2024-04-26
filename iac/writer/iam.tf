data "aws_caller_identity" "current" {}

resource "aws_iam_role" "s3_writer_role" {
  name               = "S3WriterRole"
  assume_role_policy = data.aws_iam_policy_document.s3_writer_role.json
}

data "aws_iam_policy_document" "s3_writer_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
  }
}

resource "aws_iam_policy" "s3_writer_policy" {
  name        = "S3WriterPolicy"
  description = "Policy for cross-account S3 write access"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:ListBucket",
          "s3:ListAllMyBuckets",
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ReplicateObject",
          "s3:ReplicateDelete"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:s3:::${var.source_bucket_name}/*",
        ]
      }
    ]
  })
}

