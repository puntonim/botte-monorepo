<p align="center">
  <h1 align="center">
    🟠 Botte monorepo: Botte Lambda client
  </h1>
  <p align="center">
    Just a client for Botte Backend direct Lambda invocation interface.
  <p>
</p>

<br>

⚡ Usage
=======

This Botte Lambda client is the preferred client to interact with Botte, when the
 consumer:
 - is running inside AWS infra, in the same AWS account as Botte (otherwise use [botte-http-client](../botte-http-client)))
 - can invoke Botte Lambdas: fi. if the consumer is in a VPC with no connection to
    other AWS services nor Internet access then it cannot invoke Botte Lambdas (in
    this case use [botte-dynamodb-client](../botte-dynamodb-client))

Note: you might need to set the right policy to allow the consumer to invoke Botte 
 Lambdas.

See top docstring in [http_client.py](botte_lambda_client/lambda_client.py).

Poetry install
--------------
From Github:
```sh
$ poetry add "git+https://github.com/puntonim/botte-monorepo#subdirectory=libs/public-clients/botte-lambda-client"
# at a specific version:
$ poetry add "git+https://github.com/puntonim/botte-monorepo@3da9603977a5e2948429627ac83309353cca693d#subdirectory=libs/public-clients/botte-lambda-client"
```

From a local dir:
```sh
$ poetry add "../botte-monorepo/libs/public-clients/botte-lambda-client"
$ poetry add "botte-lambda-client @ file:///Users/myuser/workspace/botte-monorepo/libs/public-clients/botte-lambda-client"
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
