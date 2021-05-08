# Tinify: A Serverless Url Shortener

This app creates a URL shortener with AWS Serverless services. All business logic is handled at the Amazon Lambda level. The basic app creates an API Gateway API, Amazon DynamoDB table for data storage. It will also create a simple ReactJs application as a demo client.

### Prerequisites

* Python3 - for backend
* Node js - for client

## The Backend

### Services Used

* Amazon API Gateway
* Amazon Lambda
* Amazon DynamoDB
* Amazon S3
* Amazon CloudFormation

### Requirements for deployment

* AWS CLI
* [AWS Chalice](https://chalice.readthedocs.io/en/stable/quickstart.html)
* Forked copy of this repository. Instructions for forking a GitHib repository can be found [here](https://help.github.com/en/github/getting-started-with-github/fork-a-repo)
* python3

### Deploying

* Create DynamoDB table from the template in /serverless directory using [cloudformation deploy](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/deploy/index.html)
* cd to /tinify-backend
  ```
  $ cd tinify-backend
  ```
* Create `.chalice/config.json`
  ```json
  {
    "version": "2.0",
    "app_name": "tinify-backend",
    "api_gateway_endpoint_type": "REGIONAL",
    "iam_policy_file": "tinify-backend-dev.json",
    "environment_variables": {
      "TABLE_NAME": "table-name-here"
    },
    "stages": {
      "dev": {
        "api_gateway_stage": "api",
        "autogen_policy": false
      }
    }
  }
  ```

* Environment Variables on your local machine
  ```bash
  export APP_TABLE_NAME=xxxxxxxxxxxxxxxxxxxx
  ```
* Tinify-backend-dev.json IAM policy
  ```json
  {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Sid": "VisualEditor0",
              "Effect": "Allow",
              "Action": [
                  "dynamodb:PutItem",
                  "dynamodb:GetItem",
                  "logs:CreateLogStream",
                  "logs:CreateLogGroup",
                  "logs:PutLogEvents"
              ],
              "Resource": [
                  "arn:*:logs:*:*:*",
                  "arn:aws:dynamodb:eu-west-1:{account-id}:table/{TABLE_NAME}"
              ]
          }
      ]
  }
  ```
* Deploy backend
  ```bash
  $ chalice deploy
  ```
* Or run locally
  ```
  $ chalice local
  ```

## The Client

* From the app root directory, cd to /tinify-frontend
  ```
  $ cd tinify-frontend
  ```
* Install packages
  ```
  yarn install
  ```
* Run the app
  ```matlab
  yarn start
  ```
* Note: you will need to provide the webserver url in /App.js file

##### Hosting

* An existing S3 bucket can be used to host the application, or create a new one
* Add the s3 bucket url location to /tinify-fronend/package.json
  ```json
    ...
    "scripts": {
      "start": "react-scripts start",
      "build": "react-scripts build",
      "test": "react-scripts test",
      "eject": "react-scripts eject",
      "deploy": "aws s3 sync build/ s3://bucket-name/tinify/"
    },
    ...
  ```
* Build the add and deploy it to S3 as static hosting
  ```coffeescript
  $ yarn build && yarn deploy
  ```
* App should be accessible at the URL similar to "example-bucket.s3-website-us-east-1.amazonaws.com"

**NOTE**: If you do not want to make bucket public, you can consider [API Gateway as a proxy for your bucket](https://docs.aws.amazon.com/apigateway/latest/developerguide/integrating-api-with-aws-services-s3.html) /tinify-frontend folder.
