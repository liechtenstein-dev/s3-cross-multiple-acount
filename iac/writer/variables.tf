variable "source_bucket_name" {
  description = "The name of the source bucket"
  type = string
}

variable "reader_account_ids" {
  description = "The account IDs of the readers"
  type = list(string)
}

variable "username" {
  description = "The name of the user that writter role will be attached to"
  type = string
}