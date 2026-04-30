module "vpc" {
    source = "terraform-aws-modules/vpc/aws"
    version = "~> 5.0"

    name = var.project_name
    cidr = var.vpc_cidr

    azs = ["us-west-2a", "us-west-2b"]
    private_subnets = var.private_subnet_cidrs
    public_subnets = var.public_subnet_cidrs

    enable_nat_gateway = false
    enable_vpn_gateway = false

    tags = {
        Name = local.name_prefix
    }
}