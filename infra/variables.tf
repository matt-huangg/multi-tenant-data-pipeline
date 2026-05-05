variable "project_name" {
  description = "Project name used for AWS resource naming and tags."
  type        = string
  default     = "ai-content-processor"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region for all regional resources."
  type        = string
  default     = "us-west-2"
}

variable "vpc_cidr" {
  description = "CIDR block for the application VPC."
  type        = string
  default     = "10.40.0.0/16"
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDR blocks for Lambda and RDS."
  type        = list(string)
  default     = ["10.40.10.0/24", "10.40.11.0/24"]
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDR blocks for NAT/bastion if needed."
  type        = list(string)
  default     = ["10.40.0.0/24", "10.40.1.0/24"]
}

variable "enable_nat_gateway" {
  description = "Whether private subnets should use NAT for public internet egress, required for worker calls to OpenAI."
  type        = bool
  default     = false
}

variable "db_name" {
  description = "Initial PostgreSQL database name."
  type        = string
  default     = "ai_content_processor"
}

variable "db_username" {
  description = "RDS master/app username."
  type        = string
  default     = "app_user"
}

variable "db_instance_class" {
  description = "RDS instance class."
  type        = string
  default     = "db.t4g.micro"
}
