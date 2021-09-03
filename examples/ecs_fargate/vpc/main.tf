
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


data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  availabilityZone_a = data.aws_availability_zones.available.names[0]
  availabilityZone_b = data.aws_availability_zones.available.names[1]
}


variable "instanceTenancy" {
  default = "default"
}

variable "dnsSupport" {
  default = true
}

variable "dnsHostNames" {
  default = true
}

variable "vpcCIDRblock" {
  default = "10.0.0.0/16"
}

variable "publicSubnetaCIDRblock" {
  default = "10.0.1.0/24"
}

variable "publicSubnetbCIDRblock" {
  default = "10.0.2.0/24"
}

variable "destinationCIDRblock" {
  default = "0.0.0.0/0"
}

variable "ingressCIDRblock" {
  type    = list
  default = ["0.0.0.0/0"]
}

variable "egressCIDRblock" {
  type    = list
  default = ["0.0.0.0/0"]
}
variable "mapPublicIP" {
  default = false
}

resource "aws_vpc" "vpc" {
  cidr_block           = var.vpcCIDRblock
  instance_tenancy     = var.instanceTenancy
  enable_dns_support   = var.dnsSupport
  enable_dns_hostnames = var.dnsHostNames
  tags = {
    Name = "${var.project_name}-${var.environment}-VPC"
  }

  lifecycle {
    ignore_changes = [tags["Changed"]]
  }  
}


resource "aws_subnet" "public_subnet_a" {
  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = var.publicSubnetaCIDRblock
  map_public_ip_on_launch = true
  availability_zone       = local.availabilityZone_a
  tags = {
    Name = "${var.project_name}-${var.environment}-public_vpc_subneta"
  }
}

resource "aws_subnet" "public_subnet_b" {
  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = var.publicSubnetbCIDRblock
  map_public_ip_on_launch = true
  availability_zone       = local.availabilityZone_b
  tags = {
    Name = "${var.project_name}-${var.environment}-public_vpc_subnetb"
  }
}

resource "aws_internet_gateway" "vpc_ig" {
  vpc_id = aws_vpc.vpc.id
  tags = {
    Name = "${var.project_name} Internet Gateway"
  }
}

resource "aws_route_table" "route_table_public" {
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block      = "0.0.0.0/0"
    gateway_id      = aws_internet_gateway.vpc_ig.id
  }

  tags = {
    Name = "${var.project_name}-${var.environment} Public Route Table"
  }
}

resource "aws_route_table_association" "publica" {
  subnet_id      = aws_subnet.public_subnet_a.id
  route_table_id = aws_route_table.route_table_public.id
}

resource "aws_route_table_association" "publicb" {
  subnet_id      = aws_subnet.public_subnet_b.id
  route_table_id = aws_route_table.route_table_public.id
}