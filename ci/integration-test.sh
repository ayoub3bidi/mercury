#!/usr/bin/env bash

echo "POSTGRES_HOST=${{ env.POSTGRES_HOST }}" > .env
echo "POSTGRES_PORT=${{ env.POSTGRES_PORT }}" >> .env
echo "POSTGRES_DB=${{ env.POSTGRES_DB }}" >> .env
echo "POSTGRES_USER=${{ env.POSTGRES_USER }}" >> .env
echo "POSTGRES_PASSWORD=${{ env.POSTGRES_PASSWORD }}" >> .env

docker-compose up --build --abort-on-container-exit mercury_integration_tests