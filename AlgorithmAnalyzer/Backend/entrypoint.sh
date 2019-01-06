#!/bin/bash

mkdir logs
touch ./logs/gunicorn.log
touch ./logs/gunicorn-access.log
tail -n 0 -f ./logs/gunicorn*.log &

exec gunicorn main:app \
    --name api \
    --bind 0.0.0.0:5000 \
    --workers 3 \
    --log-level=info \
    --log-file=./logs/gunicorn.log \
    --access-logfile=./logs/gunicorn-access.log \
	--workers=3 \
"$@"
