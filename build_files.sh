#!/bin/bash
# Vercel build step: install deps and collect static files into the directory
# Vercel serves as the /static route (see vercel.json "distDir").
set -e

pip install -r requirements.txt

# Collect admin/DRF static assets. DEBUG=0 activates the WhiteNoise
# manifest storage so filenames match what is served in production.
DEBUG=0 STATIC_ROOT="$PWD/staticfiles_build/static" \
  python app/manage.py collectstatic --noinput --clear
