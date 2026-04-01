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

resource "aws_cloudwatch_log_group" "api" {
  name              = "/${var.project_name}/api"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "worker" {
  name              = "/${var.project_name}/worker"
  retention_in_days = 30
}

resource "aws_secretsmanager_secret" "database" {
  name = "${var.project_name}/database-url"
}

resource "aws_secretsmanager_secret" "llm_api_key" {
  name = "${var.project_name}/llm-api-key"
}

data "aws_iam_policy_document" "workload" {
  statement {
    sid       = "ReadRuntimeSecrets"
    effect    = "Allow"
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [aws_secretsmanager_secret.database.arn, aws_secretsmanager_secret.llm_api_key.arn]
  }
  statement {
    sid       = "WriteApplicationLogs"
    effect    = "Allow"
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["${aws_cloudwatch_log_group.api.arn}:*", "${aws_cloudwatch_log_group.worker.arn}:*"]
  }
}

resource "aws_iam_policy" "workload" {
  name   = "${var.project_name}-workload-least-privilege"
  policy = data.aws_iam_policy_document.workload.json
}

data "aws_iam_policy_document" "irsa_assume" {
  count = var.eks_oidc_provider_arn == "" ? 0 : 1
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [var.eks_oidc_provider_arn]
    }
    condition {
      test     = "StringEquals"
      variable = "${var.eks_oidc_provider_url}:sub"
      values   = ["system:serviceaccount:${var.k8s_namespace}:${var.k8s_service_account}"]
    }
  }
}

resource "aws_iam_role" "workload" {
  count              = var.eks_oidc_provider_arn == "" ? 0 : 1
  name               = "${var.project_name}-workload"
  assume_role_policy = data.aws_iam_policy_document.irsa_assume[0].json
}

resource "aws_iam_role_policy_attachment" "workload" {
  count      = var.eks_oidc_provider_arn == "" ? 0 : 1
  role       = aws_iam_role.workload[0].name
  policy_arn = aws_iam_policy.workload.arn
}

