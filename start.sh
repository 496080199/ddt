#!/bin/sh
cd `dirname $0`&&gunicorn  -b 127.0.0.1:8000 ddt.wsgi:application