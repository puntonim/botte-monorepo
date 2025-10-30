- Progetti da cui copiare qualcosa:
  botte in patatrack
  reborn automator: il serverless + recente
  kbee-be e experiments-monorepo: il poetry + recente

----------------

- e2e tests
- committare
- client per http endpoint, non versioned
  Aggiungere in tutti i readme che non serve fare lib o clients versioned se si installano via git (e non via PiPy)
   perche si possono installare con uno specifico hash
   e che qs hash sta sempre scritto in poetry.lock
   [package.source]
    type = "git"
    url = "https://github.com/puntonim/utils-monorepo"
    reference = "HEAD"
    resolved_reference = "3da9603977a5e2948429627ac83309353cca693d"
    subdirectory = "aws-utils" 

- dynamodb interface, tests, e2e tests
- dynamodb client
  Scrivere nel readme che serve anche per vpc
    Note: the DynamoDB task Table interface is used by other services (Contabel project)
     that have no Internet access nor connection to other AWS services because they
     are in a VPC (Internet connection is not free in a VPC - and Contabel is in a VPC
     because it uses a SQLite DB on EFS which requires VPC). The solution for them
     is to use VPC Gateway Endpoint (free) to connect to DynamoDB to trigger other
     AWS services (only a few AWS services can be reached, including DynamoDB).

- sqs interface, tests, e2e tests, not deployed
- sqs client
  Scrivere nel readme che avviene il polling, meglio usare dynamodb o http

- /echo Telegram user command with webhooks

- un unico progetto (new repo aws-watchdog??) che è una Lambda che controlla 
   qualunque errore (in qualunque lambda in AWS) e me li manda via email.
   Vedi `shared-infra.cloudwatch-error-email` in patatrack-monorepo. 
   Usarlo in botte-be 

- controllare quali Lambdas ancora usano Botte in patatrack-monorepo
  e convertirle introducendo i clients di botte-be

- muovere patatrack-monorepo/projects/alarm-be to solcc-monorepo
- `sls remove` tutto patatrack-monorepo da AWS (dopo aver spostate alarm-be)
  e anche i parametri in Param Store
- archiviare git repo: patatrack-monorepo
  NB: non cancellarlo perchè c'è del codice interessante

- cambia logo al BOT su Telegram
