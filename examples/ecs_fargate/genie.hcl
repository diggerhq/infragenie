
# unified variables for use in all pipelines
variables {
  project_name = "myproj123"
  environment = "dev"
  region = "us-east-1"
}

# resource injections definition
inject {
  main_vpc = {
    source = vpc.aws_vpc.vpc # source can come from any of the pipeline steps
  }

  subnet_a = {
    source = vpc.aws_subnet.public_subnet_a
  }

  subnet_b = {
    source = vpc.aws_subnet.public_subnet_b
  }
}

pipeline {
  steps = [
    {
      name = "vpc"
      description = "creates a vpc and 4 subnets"
      source = "./vpc"
    },
    {
      name = "ecs"
      description = "creates an ecs cluster and SG"
      source = "./ecs"
    },

  ]
}
