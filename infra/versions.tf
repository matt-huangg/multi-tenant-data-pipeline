terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # TODO: Add remote state.
  # backend "s3" {
  #   bucket         = ""
  #   key            = ""
  #   region         = ""
  #   dynamodb_table = ""
  #   encrypt        = true
  # }
}
