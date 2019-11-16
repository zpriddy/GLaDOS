variable "aws_region" {
  description = "The AWS region to create things in."
  default     = "us-west-2"
}

variable "glados_bot_key" {
  description = "Slack bot key for glados"
}

variable "glados_signing_key" {
  description = "signing key for glados bot"
}