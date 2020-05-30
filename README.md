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