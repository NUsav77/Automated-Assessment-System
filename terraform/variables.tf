variable "ssh_pub_key" {
  type        = string
  description = "The pub key that will be used to ssh into the server"
}

variable "SECRET_KEY" {
  type        = string
  description = "The UUID used by django"
}