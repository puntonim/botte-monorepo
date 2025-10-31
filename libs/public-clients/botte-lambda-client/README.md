<p align="center">
  <h1 align="center">
    🌐 Botte monorepo: Botte Lambda client
  </h1>
  <p align="center">
    Just a client for Botte Backend direct Lambda invocation interface.
  <p>
</p>

<br>

⚡ Usage
=======

Use this client to interact with Botte, in AWS services inside the same AWS account
 (and with the right permission to invoke the Lambda).

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
