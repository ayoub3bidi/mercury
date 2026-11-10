#!/usr/bin/env bash

docker compose --profile test up --build --abort-on-container-exit mercury_unit_tests
