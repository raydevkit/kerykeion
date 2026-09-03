# Operação do backend Kabalah

## Desenvolvimento e testes

```bash
poetry install
poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
poetry run pytest -o addopts='' tests/test_fastapi_deployment.py tests/test_dockerfile_packaging.py
```

Variáveis aceitas: `ENVIRONMENT` (`development`, `test` ou `production`), `API_KEY`, `CORS_ORIGINS`, `HOST`, `PORT` e `GEONAMES_USERNAME`. Em produção, `API_KEY` deve ser diferente do padrão e ter ao menos 32 caracteres. `CORS_ORIGINS` é uma lista separada por vírgulas de origens HTTP(S) explícitas, sem `*`.

Depois de uma alteração intencional de dependências, atualize `poetry.lock` e exporte o lock de produção com hashes:

```bash
uvx --from poetry==2.3.1 --with poetry-plugin-export poetry export --only main --format requirements.txt --output requirements.lock
```

## Container

```bash
docker buildx build --platform linux/amd64 --build-arg VERSION=local --build-arg REVISION="$(git rev-parse HEAD)" --tag kerykeion-kabalah:local --load .
docker run --rm --name kerykeion-kabalah --env ENVIRONMENT=production --env API_KEY='<32+ caracteres aleatórios>' --publish 127.0.0.1:8000:8000 kerykeion-kabalah:local
curl http://127.0.0.1:8000/health
```

O contrato do container é TCP `8000` e `GET /health`. O `--publish` acima serve somente para validação local. Na VPS, conecte o container à rede Docker do Cloudflare Tunnel e não publique portas no host.

## Publicação e rollback

Execute manualmente o workflow **Publish container**. Ele publica `ghcr.io/raydevkit/kerykeion-kabalah:sha-<commit>` e, quando executado sobre uma tag Git, também essa tag; nunca publica `latest` e não faz deploy.

Após a publicação, obtenha o digest no GHCR e fixe a VPS em `ghcr.io/raydevkit/kerykeion-kabalah@sha256:<digest>`. Para rollback, restaure o digest anterior e recrie somente o container da API.
