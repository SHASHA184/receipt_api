#!/bin/bash

# Apply migrations to the database
docker compose exec app alembic upgrade head