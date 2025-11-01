<p align="center">
  <h1 align="center">
    🗄️ Botte monorepo: Botte DynamoDB client
  </h1>
  <p align="center">
    Just a client for Botte Backend DynamoDB interface.
  <p>
</p>

<br>

⚡ Usage
=======

This Botte DynamoDB client is the preferred client to interact with Botte, when the
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

See top docstring in [dynamodb_client.py](botte_http_client/dynamodb_client.py).

Also, see details of the DynamoDB interface in [README.md](../../../README.md) in the root dir.

Poetry install
--------------
From Github:
```sh
$ poetry add "git+https://github.com/puntonim/botte-monorepo#subdirectory=libs/public-clients/botte-dynamodb-client"
# at a specific version:
$ poetry add "git+https://github.com/puntonim/botte-monorepo@3da9603977a5e2948429627ac83309353cca693d#subdirectory=libs/public-clients/botte-dynamodb-client"
```

From a local dir:
```sh
$ poetry add "../botte-monorepo/libs/public-clients/botte-dynamodb-client"
$ poetry add "botte-dynamodb-client @ file:///Users/myuser/workspace/botte-monorepo/libs/public-clients/botte-dynamodb-client"
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
