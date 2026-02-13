variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "shy-guy"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,20}$", var.project_name))
    error_message = "project_name must be lowercase alphanumeric with hyphens, 2-21 chars, starting with a letter."
  }
}

variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "ap-northeast-1"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "prod"
}

variable "lambda_memory_size" {
  description = "Lambda function memory in MB"
  type        = number
  default     = 512

  validation {
    condition     = var.lambda_memory_size >= 128 && var.lambda_memory_size <= 3008
    error_message = "lambda_memory_size must be between 128 and 3008 MB."
  }
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 30
}

variable "creator" {
  description = "Creator tag value"
  type        = string
  default     = "terraform"
}

locals {
  name_prefix = var.project_name
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    Creator     = var.creator
    ManagedBy   = "terraform"
  }
}
