variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "project_name" {
  type    = string
  default = "secureops"
}

variable "eks_oidc_provider_arn" {
  type        = string
  default     = ""
  description = "Optional EKS OIDC provider ARN for IRSA. Leave empty when unused."
}

