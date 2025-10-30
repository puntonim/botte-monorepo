- Progetti da cui copiare qualcosa:
  botte in patatrack
  reborn automator: il serverless + recente
  kbee-be e experiments-monorepo: il poetry + recente

----------------
- use botte-http-client in e2e tests

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
  poi aggiorna docs (READMEs e architecture)

- un unico progetto (new repo aws-watchdog??) che è una Lambda che controlla 
   qualunque errore (in qualunque lambda in AWS) e me li manda via email.
   Vedi `shared-infra.cloudwatch-error-email` in patatrack-monorepo. 
   Usarlo in botte-be 
   Ocio che per deployarlo bisogna seguire un certo ordine, vedi quanto scritto in
    patatrack monorepo.

- controllare quali Lambdas ancora usano Botte in patatrack-monorepo
  e convertirle introducendo i clients di botte-be

- muovere patatrack-monorepo/projects/alarm-be to solcc-monorepo
- `sls remove` tutto patatrack-monorepo da AWS (dopo aver spostate alarm-be)
  e anche i parametri in Param Store
- archiviare git repo: patatrack-monorepo
  NB: non cancellarlo perchè c'è del codice interessante

