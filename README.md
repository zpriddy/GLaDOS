# GLaDOS - Slack Bot Framework 
GLaDOS is a Slack bot plugin framework for interactive slack bots. 

## Plugin
Every GLaDOS plugin is its own module that is imported into your main handler application. This allows GLaDOS plugins to be community based and installed as wanted just by a simple import statement. 

## Bots (GladosBot)
GLaDOS can support multiple Slack bots and applications at once. When you initialize a plugin you pass the GladosBot object of the bot you would like to be responsible for the actions of that plugin. 

## Routes and Route Types
### Route Types
Route types represent the different kind of actions GLaDOS can handle. Depending on the route type, GLaDOS will expect a different kind of payload. 

For example a SendMessage route type will be expecting a ‘channel’ field and any parameters are needed to populate the message template.

SendMessage would be called by a post request made to https://glados.io/SendMessage/{route}

However a Response route type will be expecting the raw payload from Slack. GLaDOS will then parse the payload and extract the selected ‘actionId’ form the action that was taken. The ‘actionId’ will then be used as the route for that response. 

The callback url for GLaDOS in Slack would be like: https://glados.io/Response
The same URL can be used for all the Slack bots / Applications that GLaDOS is handling. 

## Slack Payload

## Example GLaDOS Server

## AWS Deployment
### Lambda
### API Gateway
### Terraform

## Docker

## Plugins Available 

## Installation

## [Documentation](https://zpriddy.github.io/GLaDOS/index.html) 


Because of this I would recommend prefixing the routes with the plugin name to make it clear of the routing of that call. GLaDOS
