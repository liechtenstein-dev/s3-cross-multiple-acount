provider "aws" {
  region = "us-east-2"
}

resource "aws_iam_role" "s3_reader_role" {
  name        = "S3ReaderRole"
  description = "Role for cross-account S3 read access"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          AWS = "arn:aws:iam::${var.writer_account_id}:root"
        }
        Effect = "Allow"
      }
    ]
  })
}
resource "aws_iam_policy" "s3_role_reader_policy" {
  name = "S3ReaderPolicy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowS3ReaderRole"
        Effect    = "Allow"
        Action    = [
            "s3:ListBucket",
            "s3:ListAllMyBuckets",
            "s3:GetObject",
            "s3:PutObject",
            "s3:DeleteObject",
            "s3:ReplicateObject",
            "s3:PutObjectACL",
            "s3:ReplicateDelete"
        ]
        Resource  = [
          "arn:aws:s3:::*",
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "s3_reader_role_attachment" {
  role       = aws_iam_role.s3_reader_role.name
  policy_arn = aws_iam_policy.s3_role_reader_policy.arn
}