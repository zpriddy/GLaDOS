data "aws_iam_policy_document" "policy" {
  statement {
    sid    = "ALambda"
    effect = "Allow"

    principals {
      identifiers = [
        "lambda.amazonaws.com"]
      type        = "Service"
    }

    actions = [
      "sts:AssumeRole"]
  }

}

data "aws_iam_policy_document" "logging_policy" {
  statement {
    sid    = "ALogging"
    effect = "Allow"

    actions   = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:DescribeLogGroups",
      "logs:DescribeLogStreams",
      "logs:PutLogEvents",
    ]
    resources = [
      "*"]
  }
}

resource "aws_iam_policy" "logging_policy" {
  name   = "glados_logging_policy"
  policy = data.aws_iam_policy_document.logging_policy.json
}

resource "aws_iam_role" "glados_lambda_iam" {
  name               = "glados_lambda_iam"
  assume_role_policy = data.aws_iam_policy_document.policy.json
  tags               = {
    Owner = "Glados"
  }
}

resource "aws_iam_role_policy_attachment" "logging_policy_attachment" {
  role       = aws_iam_role.glados_lambda_iam.name
  policy_arn = aws_iam_policy.logging_policy.arn
}

