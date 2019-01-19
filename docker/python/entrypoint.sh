#!/bin/bash
set -e

# apply migrations
#make migrate

# Collect static files
#make collect_static

exec "$@"
