<p align="center">
  <h1 align="center">
    🌐 Botte monorepo: Botte DynamoDB Tasks
  </h1>
  <p align="center">
    Just schemas for DynamoDB task queues in Botte.
  <p>
</p>

<br>

⚡ Usage
=======

Used by [botte-dynamodb-client](../public-clients/botte-dynamodb-client), with [aws-dynamodb-client](https://github.com/puntonim/clients-monorepo/tree/main/aws-dynamodb-client),
 to interact with Botte via its DynamoDB interface.

Botte has a DynamoDb interface meant to be used by consumers that:
 - are running in AWS infra, in the same AWS account as Botte (otherwise they would use [botte-http-client](../botte-http-client))
 - but cannot invoke Botte Lambdas directly, fi. they are in a VPC with no connection to
    other AWS services nor Internet access (otherwise they would use [botte-lambda-client](../botte-lambda-client))

Note: one of my patterns is to have Lambdas that connect to a SQLite database stored
 on EFS. EFS requires a VPC, and the Lambda to be in the same VPC. But, for VPCs, 
 connection to the Internet and other AWS services requires expensive things like
 internet gateway, NAT or PrivateLink. But VPCs can connect to DynamoDB and S3 (only
 these 2 services) via a VPC Gateway Endpoint for free. So in the end: a Lambda in
 a VPC can connect to Botte DynamoDB interface by using a free VPC Gateway Endpoint
 and this Botte DynamoDB client.

This lib provides means to create and parse tasks to be read and written to Botte
 DynamoDB task queue.

See top docstring in [botte_message_dynamodb_task.py](botte_dynamodb_tasks/botte_message_dynamodb_task.py)

Poetry install
--------------
From Github:
```sh
$ poetry add "git+https://github.com/puntonim/botte-monorepo#subdirectory=libs/botte-dynamodb-tasks"
# at a specific version:
$ poetry add "git+https://github.com/puntonim/botte-monorepo@3da9603977a5e2948429627ac83309353cca693d#subdirectory=libs/botte-dynamodb-tasks"
```

From a local dir:
```sh
$ poetry add "../botte-monorepo/libs/botte-dynamodb-tasks"
$ poetry add "botte-dynamodb-tasks @ file:///Users/myuser/workspace/botte-monorepo/libs/botte-dynamodb-tasks"
```

Pip install
-----------
Same syntax as Poetry, but change `poetry add` with `pip install`.


🛠️ Development setup
====================

See [README.md](../../README.md) in the `lib` dir.


🚀 Deployment
=============

*Not deployed* as it can be (pip-)installed directly from Github o local dir 
 (see Usage section).\
And *not versioned* as when (pip-)installing from Github, it is possible to choose
 any version with a hash commit (see Usage section).


🔨 Test
======

```sh
$ make test
```


©️ Copyright
=============

Copyright puntonim (https://github.com/puntonim). No License.
