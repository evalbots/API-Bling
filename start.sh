#!/usr/bin/env bash
# Instala o Chromium e dependências
playwright install --with-deps chromium

# Inicia o Uvicorn, usando a porta que o Railway fornece
uvicorn bling_redirect_api:app --host 0.0.0.0 --port ${PORT:-8000}
