output "role_arn" {
  value = aws_iam_role.s3_reader_role.arn
}

output "exit_code_lst" {
  value = module.shell[*].exit_code
}