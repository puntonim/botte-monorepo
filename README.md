<p align="center">
  <img src="docs/img/img.png" height="350"></a>
  <h1 align="center">
    Botte monorepo
  </h1>
  <p align="center">
    A project, Botte Backend, and a collection of clients for its interfaces,
     plus libs.<br>
    Botte is just an over-engineered 🤓 bot that sends messages to me, via Telegram for now.
  <p>
</p>

<br>

In this monorepo there are 2 categories of software:
- 📚 `libs`: standalone Python libs that can be installed individually from the Git subdir.
  - `libs/*`: eg. `libs/botte-dynamodb-tasks`. Used only by projects/libs in this
    monorepo.
  - `libs/public-clients/*`: eg. `libs/public-clients/botte-http-client`. Clients 
     for Botte Backend interfaces, meant to be used outside this repo.
- 💡 `projects`: only `projects/botte-be` for now. Deployed as (a set of) Lambdas.


📐 Architecture
================

The backend, [botte-be project](projects/botte-be), is a set of Lambda functions triggered:
 - via [Lambda direct invocation](libs/public-clients/botte-lambda-client): to be used by
    consumers in AWS ingra, in the same AWS account as Botte, that can invoke Botte Lambdas (with the right invoke policy permissions);
 - via [HTTPS](libs/public-clients/botte-http-client) with a secret auth token: 
    to be used by any consumer with Internet access and outside AWS infra (and maybe, in the future, by Telegram webhook configured for
    Telegram user commands like `/echo`, see the old, and now 
    archived [patatrack-monorepo](https://github.com/puntonim/patatrack-monorepo); do not use this in a AWS service, but rather
    prefer the Lambda direct invocation or DynamoDB task table;
 - via [DynamoDB task Table](libs/public-clients/botte-dynamodb-client): to be used by Lambda
    consumers that are inside a VPC that has no Internet connection nor connection to other AWS services (so they cannot use
    the HTTP or Lambda interface - Internet connection in a VPC is not free, nor connection to AWS services different than DynamoDB and S3) but have a free
    VPC Gateway Endpoint to DynamoDB; example: the old, and now archived, Contabel
    project in [patatrack-monorepo](https://github.com/puntonim/patatrack-monorepo)
    that was inside a VPC because it used a SQLite DB in EFS (and EFS requires a VPC);
 - via [SQS task Queue](libs/public-clients/botte-sqs-client): no consumers yet - 
    COMMENTED OUT because it incurs a little cost.

Each of the interfaces has a client distributed in this repo, see `Usage` section.

The Telegram's and HTTP's secrets are stored in Parameters Store.

No database.

![architecture-draw.io.svg](./docs/img/architecture-draw.io.svg)


*SQS queues commented out to avoid costs*
-----------------------------------------
I commented out the SQS task queues interface to avoid costs in AWS and because unused
 yet.

SQS is charged by (million) requests per month (and the first 1M is free).\
Note: requests and NOT messages.

A Lambda triggered by an SQS generates 15 requests per minutes by polling (and getting
 empty receives most of the time).\
This means 15*60*24*30=648k requests/month.

So 1 SQS+Lambda is free, but more than that will incur costs.\
In a case (old Patatrack monorepo) with 3 SQS I was charged around $0.30 a month.

The free alternative to the general usage of SQS is to use SNS + Lambda or
 DynamoDB Table + Stream + Lambda.\
They both use notifications instead of polling.

Btw: the solution DynamoDB Table + Stream + Lambda also solves the problem of a Lambda
 in a VPC (and without connection to the Internet or to other AWS services - because
 Internet connection in a VPC is not free ) that needs to trigger another Lambda
 (outside the VPC) that has Internet access. Example: see Botte and Fritarol in the
 old, and now archived,
 [patatrack-monorepo](https://github.com/puntonim/patatrack-monorepo).


⚡ Usage
=======

This monorepo offers 4 [clients](libs/public-clients) to interact with Botte, one for each interface.


Lambda client for Lambda Interface
----------------------------------
This [botte-lambda-client](libs/public-clients/botte-lambda-client) is the preferred client to interact with Botte, when the
 consumer:
 - is running inside AWS infra, in the same AWS account as Botte (otherwise use [botte-http-client](../botte-http-client)))
 - can invoke Botte Lambdas: fi. if the consumer is in a VPC with no connection to
    other AWS services nor Internet access then it cannot invoke Botte Lambdas (in
    this case use [botte-dynamodb-client](../botte-dynamodb-client))

Note: you might need to set the right policy to allow the consumer to invoke Botte 
 Lambdas.


You can also use this interface by invoking the Lambda directly in the AWS website,
 using `aws-cli`, using Python and `boto3`.

The payload to be sent is:
```py
{
    "text": "Hello world from aws-lambda-client pytests!",
    "sender_app": "AWS_LAMBDA_CLIENT"  # sender_app is optional.
}
```

HTTP client for HTTP Interface
------------------------------
This [botte-http-client](libs/public-clients/botte-http-client)
 is the preferred client to interact with Botte, when the
 consumer:
 - has Internet access
 - and is NOT running inside AWS infra or NOT the same AWS account as Botte (otherwise use [botte-lambda-client](../botte-lambda-client))

You can also use this interface with curl or any other HTTP client.

Example with curl:
```sh
$ curl -X POST https://5t325uqwq7.execute-api.eu-south-1.amazonaws.com/message \
   -H 'Authorization: XXX' \
   -d '{"text": "Hello World", "sender_app": "CURL_TEST"}'  # sender_app is optional.
{
  "message_id": 8,
  "from": {
    "id": 6570886232,
    "is_bot": true,
    "first_name": "Botte",
    "username": "realbottebot"
  },
  "chat": {
    "id": 2137200685,
    "first_name": "Paolo",
    "username": "punto...",
    "type": "private"
  },
  "date": 1698264386,
  "text": "Hello World"
}
```

DynamoDB client for DynamoDB task Table Interface
-------------------------------------------------
This [botte-dynamodb-client](libs/public-clients/botte-dynamodb-client) is the preferred client to interact with Botte, when the
 consumer:
 - is running in AWS infra, in the same AWS account as Botte (otherwise use [botte-http-client](../botte-http-client))
 - but it cannot invoke Botte Lambdas directly, fi. it is in a VPC with no connection to
    other AWS services nor Internet access (otherwise use [botte-lambda-client](../botte-lambda-client))

Note: one of my patterns is to have Lambdas that connect to a SQLite database stored
 on EFS. EFS requires a VPC, and the Lambda to be in the same VPC. But, for VPCs, 
 connection to the Internet and other AWS services requires expensive things like
 internet gateway, NAT or PrivateLink. But VPCs can connect to DynamoDB and S3 (only
 these 2 services) via a VPC Gateway Endpoint for free. So in the end: a Lambda in
 a VPC can connect to Botte DynamoDB interface by using a free VPC Gateway Endpoint
 and this Botte DynamoDB client.

You can also use this interface with DynamoDB webpage (AWS console website), `aws-cli` or `boto3` with Python

The format of the task to write to DynamoDb is:
```json
{
    "PK": {
        "S": "BOTTE_MESSAGE"
    },
    "SK": {
        "S": "34sVCw69dftbK1MSWtRkv6T8vGp"
    },
    "ExpirationTs": {
        "N": "1762002142"
    },
    "Payload": {
        "M": {
            "text": {
                "S": "Hello world!"
            }
        }
    },
    "SenderApp": {
        "S": "BOTTE_DYNAMODB_CLIENT_PYTESTS"
    },
    "TaskId": {
        "S": "BOTTE_MESSAGE"
    }
}
```

SQS task Queue Interface
------------------------
TODO ..............

COMMENTED OUT because it incurs a little cost.


💬 Telegram configuration
=========================

Create a Bot, get a token and your chat_id
------------------------------------------

The first step is the creation of the new bot with Telegram. Do it by sending
 the message `/newbot` to `@BotFather`, as stated in the docs:
https://core.telegram.org/bots/tutorial#obtain-your-bot-token
The response will include a token to be stored in AWS Parameter Store 
 (see [README.md](projects/botte-be/README.md) in botte-be).

The bot should be able to send messages to your target profile (`@punto...` in my case):
 in order to do so you have to send a message from your target profile to the bot
 (so initiate a conversation).

Finally, you need to know the `chat_id` of your target profile (`@punto...` in my case): 
 to do so the quickest way is to send a message to `@JsonDumpBot` and keep track of
 `message.chat.id`. Then store it in `./botte/conf/settings` in 
 `settings.PUNTONIM_CHAT_ID`.

Set the webhook for Telegram user commands
------------------------------------------
In the future, we might want to handle  Telegram user commands like `/echo`, via
 webhooks. In this case see what done in the old, and now archived,
 [botte project](https://github.com/puntonim/patatrack-monorepo/tree/main/projects/botte#set-the-webhook-for-user-commands)
 in patatrck-monorepo.



©️ Copyright
=============

Copyright puntonim (https://github.com/puntonim). No License.
