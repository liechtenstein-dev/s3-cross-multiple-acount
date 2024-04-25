data "aws_iam_user" "caller_user" {
  user_name = var.username
}