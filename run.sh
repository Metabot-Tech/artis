#!/bin/sh

sleep 10
alembic upgrade head
python app.py