resource "aws_api_gateway_rest_api" "glados_example_api" {
  name        = "glados_example_api"
  description = "REST API GLaDOS"
}

###################################################################################################
# Shared Paths
###################################################################################################

resource "aws_api_gateway_resource" "events" {
  parent_id   = aws_api_gateway_rest_api.glados_example_api.root_resource_id
  path_part   = "Events"
  rest_api_id = aws_api_gateway_rest_api.glados_example_api.id
}

resource "aws_api_gateway_resource" "slash" {
  parent_id   = aws_api_gateway_rest_api.glados_example_api.root_resource_id
  path_part   = "Slash"
  rest_api_id = aws_api_gateway_rest_api.glados_example_api.id
}

resource "aws_api_gateway_resource" "interaction" {
  parent_id   = aws_api_gateway_rest_api.glados_example_api.root_resource_id
  path_part   = "Interaction"
  rest_api_id = aws_api_gateway_rest_api.glados_example_api.id
}

resource "aws_api_gateway_resource" "send_message_root" {
  parent_id   = aws_api_gateway_rest_api.glados_example_api.root_resource_id
  path_part   = "SendMessage"
  rest_api_id = aws_api_gateway_rest_api.glados_example_api.id
}

###################################################################################################
# Menu Path
###################################################################################################

resource "aws_api_gateway_resource" "menu" {
  parent_id   = aws_api_gateway_rest_api.glados_example_api.root_resource_id
  path_part   = "Menu"
  rest_api_id = aws_api_gateway_rest_api.glados_example_api.id
}

resource "aws_api_gateway_method" "menu" {
  rest_api_id   = aws_api_gateway_rest_api.glados_example_api.id
  resource_id   = aws_api_gateway_resource.menu.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "menu" {
  integration_http_method = "POST"
  resource_id             = aws_api_gateway_resource.menu.id
  rest_api_id             = aws_api_gateway_rest_api.glados_example_api.id
  http_method             = aws_api_gateway_method.menu.http_method
  type                    = "AWS_PROXY"
  uri                     = module.lambda_function.invoke_arn
}

###################################################################################################
# Send Message
###################################################################################################

resource "aws_api_gateway_resource" "send_message" {
  parent_id   = aws_api_gateway_resource.send_message_root.id
  path_part   = "{route+}"
  rest_api_id = aws_api_gateway_rest_api.glados_example_api.id
}

resource "aws_api_gateway_method" "send_message" {
  rest_api_id   = aws_api_gateway_rest_api.glados_example_api.id
  resource_id   = aws_api_gateway_resource.send_message.id
  http_method   = "POST"
  authorization = "NONE"

  request_parameters = {
    "method.request.path.route" = true
  }
}

resource "aws_api_gateway_integration" "send_message" {
  integration_http_method = "POST"
  resource_id             = aws_api_gateway_resource.send_message.id
  rest_api_id             = aws_api_gateway_rest_api.glados_example_api.id
  http_method             = aws_api_gateway_method.send_message.http_method
  type                    = "AWS_PROXY"
  uri                     = module.lambda_function.invoke_arn

  request_parameters = {
    "integration.request.path.route" = "method.request.path.route"
  }
}

resource "aws_api_gateway_deployment" "deployment" {
  depends_on = [
    "aws_api_gateway_integration.menu",
    "aws_api_gateway_integration.send_message",
  ]
  rest_api_id = aws_api_gateway_rest_api.glados_example_api.id
  stage_name  = "prod"
}