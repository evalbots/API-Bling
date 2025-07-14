#!/bin/bash
playwright install --with-deps chromium
uvicorn bling_redirect_api:app --host 0.0.0.0 --port ${PORT:-8000}
