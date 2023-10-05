# Mercury ⚡️ 
A FastApi template with PostgreSQL & Redis.

## Prepare configurations

```shell
cp .env.dist .env
```

## Run the containers

```shell
docker-compose up --build --force-recreate
```

## Test the database

```shell
$ docker exec -it mercury_db psql -U mercury mercury
psql (13.9 (Debian 13.9-1.pgdg110+1))
Type "help" for help.
```

## Test the API

You can check the Swagger doc here: http://localhost:8000

```shell
$ curl localhost:5002/v1/health
{"alive":true,"ip":"172.21.0.1","status":"ok"}
```