resource "null_resource" "pip" {
  provisioner "local-exec" {
    command = "cd ${path.module}/src && ./build.sh"
  }
  triggers = {
    uuid = uuid()
  }
}

module "lambda_function" {

  source = "github.com/raymondbutcher/terraform-aws-lambda-builder"

  # Standard aws_lambda_function attributes.
  function_name = "glados"
  handler       = "lambda.handler"
  runtime       = "python3.7"
  timeout       = 30

  # Enable build functionality.
  build_mode = "FILENAME"
  filename = "${path.module}/package.zip"
  source_dir = "${path.module}/build"
  role = aws_iam_role.glados_lambda_iam.arn

  # Create and use a role with CloudWatch Logs permissions.
  # role_cloudwatch_logs = true

  environment = {
    variables = {
      glados_bot_key = var.glados_bot_key
      glados_signing_key = var.glados_signing_key
    }
  }
}

resource "aws_cloudwatch_log_group" "glados" {
  name              = "/aws/lambda/glados"
  retention_in_days = 14
}

resource "aws_lambda_permission" "glados" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "${module.lambda_function.function_name}"
  principal     = "apigateway.amazonaws.com"

  # More: http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html
  source_arn = "arn:aws:execute-api:us-west-2:231038321568:*/*/*/*"

}