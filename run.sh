#!/bin/sh

sleep 10
alembic upgrade head
python src/app.py
