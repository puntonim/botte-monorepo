- Progetti da cui copiare qualcosa:
  botte in patatrack
  reborn automator: il serverless + recente
  kbee-be e experiments-monorepo: il poetry + recente

----------------
- sqs interface, tests, e2e tests, not deployed
- sqs client
  Scrivere nel readme che avviene il polling, meglio usare dynamodb o http

- /echo Telegram user command with webhooks
  poi aggiorna docs (READMEs e architecture)

- un unico progetto (new repo aws-watchdog??) che è una Lambda che controlla 
   qualunque errore (in qualunque lambda in AWS) e me li manda via email.
   C'è già qualcosa in serverless.yml, cerca "# TODO aws-watchdog"
   Vedi `shared-infra.cloudwatch-error-email` in patatrack-monorepo. 
   Usarlo in botte-be (in tutte le Lambda, Dynamodb, SQS)
   Ocio che per deployarlo bisogna seguire un certo ordine, vedi quanto scritto in
    patatrack monorepo.

- controllare quali Lambdas ancora usano Botte in patatrack-monorepo
  e convertirle introducendo i clients di botte-be

- muovere patatrack-monorepo/projects/alarm-be to solcc-monorepo
- `sls remove` tutto patatrack-monorepo da AWS (dopo aver spostate alarm-be)
  e anche i parametri in Param Store
- archiviare git repo: patatrack-monorepo
  NB: non cancellarlo perchè c'è del codice interessante

