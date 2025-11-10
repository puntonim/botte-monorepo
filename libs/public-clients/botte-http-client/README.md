<p align="center">
  <h1 align="center">
    🌐 Botte monorepo: Botte HTTP client
  </h1>
  <p align="center">
    Just a client for Botte Backend HTTP interface.
  <p>
</p>

<br>

⚡ Usage
=======

This Botte HTTP client is the preferred client to interact with Botte, when the
 consumer:
 - has Internet access
 - and is NOT running inside AWS infra or NOT the same AWS account as Botte (otherwise use [botte-lambda-client](../botte-lambda-client))

Note: when the consumer is running in AWS infra (fi. Lambda), the preferred client
 should be [botte-lambda-client](../botte-lambda-client).

See top docstring in [http_client.py](botte_http_client/http_client.py).

Also, see details of the HTTP interface in [README.md](../../../README.md) in the root dir.

Poetry install
--------------
From Github:
```sh
$ poetry add "git+https://github.com/puntonim/botte-monorepo#subdirectory=libs/public-clients/botte-http-client"
# at a specific version:
$ poetry add "git+https://github.com/puntonim/botte-monorepo@3da9603977a5e2948429627ac83309353cca693d#subdirectory=libs/public-clients/botte-http-client"
```

From a local dir:
```sh
$ poetry add "../botte-monorepo/libs/public-clients/botte-http-client"
$ poetry add "botte-http-client @ file:///Users/myuser/workspace/botte-monorepo/libs/public-clients/botte-http-client"
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
