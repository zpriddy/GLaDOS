# GLaDOS - Slack Bot Framework 
GLaDOS is a Slack bot plugin framework for interactive slack bots. 

Do you have a bunch of Slack Bots and are tired of spinning up new infrastructure each time you want to deploy a new 
bot?

GLaDOS allows you to have one set of deployed infrastructure that multiple Slack bots can run on at once. This helps 
simplifies your infrastructure and deployment. 


## Installation
The easiest way to install GLaDOS is using pip:
```bash
pip3 install glados
```

## Example GLaDOS Server

## AWS Deployment
GLaDOS is designed to be deployed in an AWS environment in production. This repo includes sample Terraform deployment
scripts that can be used to deploy all of the required infrastructure for a GLaDOS deployment.

#### AWS Lambda
The main part GLaDOS runs in Lambda in AWS.

#### API Gateway
AWS API Gateway is how slack and your webhooks interact with GLaDOS.

#### Postgres
Postgres is used to store past state information for referencing data.

## Docker
Work is in progress to make GLaDOS run in Docker.

## Plugins Available 

## [Documentation](https://zpriddy.github.io/GLaDOS/index.html) 

—
## GLaDOS Plugin
Every GLaDOS plugin is its own module that is imported into your main handler application. This allows GLaDOS plugins to be community based and installed as wanted just by a simple import statement. 

V2: Each GLaDOS Plug-in has to have the register_plugin decorator and match the Plugin Interface. The easiest way to do this is to use the Plugin Class that is provided with GLaDOS. In the main GLaDOS function you will have to import all of your plugin modules and kick off a scan for plugins. This same method applies for GLaDOS Bots. 

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