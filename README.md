# Mercury
<center>
    <img src="./src/assets/mercury-logo.png"/> <br>
    A simple FastApi template.
</center>

## Main purpose of this project
Mercury provide you a simple and reliable boilerplate that anyone can use from beginners to experts (no deep bullsh*t).   

This project uses basic [OAuth2]() authentication provided by FastApi security nested package, [PostgreSQL]() as its main database, [Redis]() for caching, and [flyway]() for database migration.

## Setup
### Environment variables

```shell
cp .env.dist .env
```
This will create a `.env` file in your project locally.
```
APP_TITLE = "Mercury API Docs"
APP_DESCRIPTION = "This is the Swagger documentation of the Mercury API"
APP_VERSION = 1.0
API_VERSION = "v1"
APP_ENV=local
## Admin Configuration
ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin"
ADMIN_PASSWORD = "admin"
## Postgres Configuration
POSTGRES_HOST_AUTH_METHOD = changeit
POSTGRES_PASSWORD = mercury
POSTGRES_HOST = mercury_db
POSTGRES_PORT = 5432
POSTGRES_USER = mercury
POSTGRES_DB = mercury
POSTGRES_HOST_AUTH_METHOD = trust
## Redis Configuration
REDIS_HOST = mercury_cache
REDIS_PORT = 6379
## JWT Configuration
JWT_SECRET_KEY = "mysecretkey"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

### Run the containers
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

You can check the Swagger documentation on http://localhost:8000.

```shell
$ curl localhost:5002/v1/health
{"alive":true,"ip":"172.21.0.1","status":"ok"}
```

## How to add new SQL migrations ?
One of the main principles of this project is to `Keep things simple`. That's why we do not have any fancy ORM package installed here.  
To add a new migration to your project simply add a new SQL file in the `migrations` folder along with the next version number at the beginning of file name.  
```
CREATE TABLE IF NOT EXISTS public.test (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(200)
);
-- This is an example where we create a test table. The new file name will be "V1.3__add_test_table"
```