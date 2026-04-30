terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # This project intentionally uses local state for now because it is a solo
  # side project. Add an S3 backend when multiple people, machines, or CI/CD
  # need to run Terraform against the same infrastructure.
  # backend "s3" {
  #   bucket         = ""
  #   key            = ""
  #   region         = ""
  #   dynamodb_table = ""
  #   encrypt        = true
  # }
}
