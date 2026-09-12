# Minimal illustrative IaC. Run via GitLab's Terraform integration
# (terraform:plan / terraform:apply jobs) with a GitLab-managed remote
# state backend (http backend using CI_JOB_TOKEN).

terraform {
  required_version = ">= 1.5"

  backend "http" {}

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "environment" {
  description = "dev, uat, or prod"
  type        = string
}

variable "app_name" {
  default = "enterprise-python-demo"
}

provider "aws" {
  region = "us-east-1"
}

# Example: an ECR repository per environment for the Docker image.
resource "aws_ecr_repository" "app" {
  name                 = "${var.app_name}-${var.environment}"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}
