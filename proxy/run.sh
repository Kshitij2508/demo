#!/bin/sh
set -e

# Replace environment variables in the Nginx config template
envsubst  < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf
nginx -g 'daemon off;'