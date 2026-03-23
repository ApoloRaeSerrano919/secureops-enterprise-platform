terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_ecr_repository" "api" {
  name = "${var.project_name}-api"
  image_scanning_configuration { scan_on_push = true }
}

resource "aws_ecr_repository" "event_gateway" {
  name = "${var.project_name}-event-gateway"
  image_scanning_configuration { scan_on_push = true }
}

