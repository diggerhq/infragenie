
terraform {
  required_version = ">= 0.12"
}

provider "aws" {
  # version = "= 3.45.0"
  region  = var.region
  # profile = var.aws_profile
  # access_key = var.aws_key
  # secret_key = var.aws_secret  
}

resource "aws_ecs_cluster" "app" {
  name = var.project_name
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_security_group" "ecs_service_sg" {
  name_prefix = "${var.project_name}-${var.environment}"
  description = "Security group shared by all ECS services"
  vpc_id      = data.aws_vpc.main_vpc.id
}

