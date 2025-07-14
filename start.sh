#!/bin/bash
echo "Starting Container"

# Instala o Chromium com dependências via Playwright
npx playwright install --with-deps chromium

# Inicia o servidor com Uvicorn na porta definida pela variável de ambiente PORT (padrão 8000)
uvicorn bling_redirect_api:app --host 0.0.0.0 --port ${PORT:-8000}
