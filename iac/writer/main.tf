resource "aws_iam_policy" "s3_writer_policy" {
  name        = "S3WriterPolicy"
  description = "Policy for cross-account S3 write access"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Effect   = "Allow"
        Resource = [
          "arn:aws:s3:::${var.source_bucket_name}/*",
        ]
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "s3_writer_user_attach" {
  user       = data.aws_iam_user.caller_user.user_name
  policy_arn = aws_iam_policy.s3_writer_policy.arn
}
