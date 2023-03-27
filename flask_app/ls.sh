#!/bin/bash

set -e

flask db init || true 
flask db migrate
flask db upgrade
exec "$@"
