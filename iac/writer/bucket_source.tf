data "aws_s3_bucket" "bucket_source" {
  count  = var.create_bucket == false ? 1 : 0
  bucket = var.source_bucket_name
}

data "aws_iam_policy_document" "s3_policy_bucket" {
  statement {
    sid    = "AllowS3ReaderRole"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = [for i in var.reader_account_ids : "arn:aws:iam::${i}:root"]
    }
    actions = [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket",
        "s3:DeleteObject",
        "s3:PutObjectACL",
        "s3:GetBucketLocation"
    ]
    resources = [
      "arn:aws:s3:::${var.source_bucket_name}",
      "arn:aws:s3:::${var.source_bucket_name}/*",
    ]
  }

}

module "s3_bucket" {
  count                    = var.create_bucket == true ? 1 : 0
  source                   = "terraform-aws-modules/s3-bucket/aws"
  bucket                   = var.source_bucket_name
  attach_policy            = true
  acl                      = "private"
  control_object_ownership = true
  object_ownership         = "ObjectWriter"
  versioning = {
    enabled = true
  }
  policy = data.aws_iam_policy_document.s3_policy_bucket.json
}