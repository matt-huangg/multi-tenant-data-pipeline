module "jobs_queue" {
  source  = "terraform-aws-modules/sqs/aws"
  version = "~> 4.0"

  name = "${local.name_prefix}-jobs"

  fifo_queue = false
  create_dlq = true

  redrive_policy = {
    maxReceiveCount = 3
  }

  tags = local.tags
}
