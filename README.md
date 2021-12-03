
# :genie: InfraGenie

InfraGenie is a tool that allows you to split your infrastructure project into separate independent pieces, each with their own terraform state. This is done by using [terraform data blocks](https://www.terraform.io/docs/language/data-sources/index.html) behind the scenes to simulate a pattern similar to dependency injection in programming languages.

![infragenie drawio (3)](https://user-images.githubusercontent.com/1627972/132094461-6d07d7ab-0ea9-4da5-a0ff-1f1d3ae6637f.png)

## Why this pattern?

There are several reasons why you would want to adopt this pattern:

1. Flexibility in customising your infrastructure. We know that for a single project the infrastructure might change from one environment to another. For example if you are using an Elasticsearch service in production you might use a self-hosted version in dev to save costs. InfraGenie makes this process very easy
2. Split your terraform state. By splitting your state accross several modules you can run several applies in parallel. It makes the terraform refresh faster. It also makes your applies safer since if some apply goes haywire it will only affect the resources in the current module.

**What about Terraform modules?**

Terraform modules can allow you to acheive some flexibiliy buy you still share state across the entire project. It is more difficult to make part of a module optional. The `count` syntax and similar `foreach` declarative statements in terraform can be confusing if you are not used to the declarative style it uses.

## How it works

To use infragenie you simply create a file called `genie.hcl` in the root of your project and use it to define your pipeline.

```hcl
# genie.hcl


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
}

pipeline {
  steps = [
    {
      name = "vpc"
      description = "creates a vpc and 2 subnets"
      source = "./vpc"
    },
    {
      name = "ecs"
      description = "creates an ecs cluster and SG"
      source = "./ecs"
    },
  ]
}
```

Now with this genie file you can use the vpc in any of your modules as a data definition:

```hcl
# ecs/main.tf

resource "aws_security_group" "ecs_service_sg" {
  # using global variables
  name_prefix = "${var.project_name}-${var.environment}"
  # using vpc from other module as data block
  vpc_id      = data.aws_vpc.main_vpc.id
}
```

## Quickstart

You can install InfraGenie CLI via pip

```shell
pip install infragenie
```

## Usage

You can use the examples to try out infragenie:

Clone the repository:

```shell
git clone https://github.com/diggerhq/infragenie
cd infragenie/examples/ecs_fargate
```

export your AWS keys:

```shell
export AWS_ACCESS_KEY_ID=<Access Key>
export AWS_SECRET_ACCESS_KEY=<Secret>
```

Use igm to apply the example:

```shell
igm apply
```

take note of the generated `.infragenie` directory along with all the generated data. After exploration you can destroy the resources with:

```shell
igm destroy
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please start the project if you think other people will also find it useful.

## License

[MIT](https://choosealicense.com/licenses/mit/)
