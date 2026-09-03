# Operação do backend Kabalah

## Desenvolvimento e testes

```bash
poetry install
poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
poetry run pytest -o addopts='' tests/test_fastapi_deployment.py tests/test_dockerfile_packaging.py
```

Variáveis aceitas: `ENVIRONMENT` (`development`, `test` ou `production`), `API_KEY`, `CORS_ORIGINS`, `HOST`, `PORT`, `APP_VERSION`, `GIT_REVISION` e `GEONAMES_USERNAME`. Em produção, `API_KEY` deve ser diferente do padrão e ter ao menos 32 caracteres, e `GIT_REVISION` deve ser o SHA Git hexadecimal completo de 40 caracteres. Revisões hexadecimais maiúsculas são normalizadas para minúsculas. Desenvolvimento e teste aceitam valores locais como `unknown` e `local-test`. `CORS_ORIGINS` é uma lista separada por vírgulas de origens HTTP(S) explícitas, sem `*`.

Depois de uma alteração intencional de dependências, atualize `poetry.lock` e exporte o lock de produção com hashes:

```bash
uvx --from poetry==2.3.1 --with poetry-plugin-export==1.10.0 poetry export --only main --format requirements.txt --output requirements.lock
```

O CI executa esse mesmo export e compara o resultado byte a byte com `requirements.lock`.

## Container

```bash
docker buildx build --platform linux/amd64 --build-arg VERSION=local --build-arg REVISION="$(git rev-parse HEAD)" --tag kerykeion-kabalah:local --load .
docker run --rm --name kerykeion-kabalah --env API_KEY='<32+ caracteres aleatórios>' --publish 127.0.0.1:8000:8000 kerykeion-kabalah:local
curl http://127.0.0.1:8000/health
```

O container define `ENVIRONMENT=production` por padrão e encerra na inicialização se `API_KEY` estiver ausente, for a chave padrão ou tiver menos de 32 caracteres, ou se `GIT_REVISION` não for um SHA completo. O `Dockerfile` mantém placeholders para permitir a construção local, mas eles não iniciam em produção. Para executar a imagem deliberadamente em desenvolvimento ou teste, passe `--env ENVIRONMENT=development` ou `--env ENVIRONMENT=test`.

O contrato do container é TCP `8000` e `GET /health`. O `--publish` acima serve somente para validação local. Na VPS, conecte o container à rede Docker do Cloudflare Tunnel e não publique portas no host. Os argumentos `VERSION` e `REVISION` são expostos como metadados de runtime; `/` aponta para `https://github.com/raydevkit/kerykeion/tree/<SHA completo>`. `APP_VERSION` continua aceitando rótulos como `dev`, `local`, `ci` e versões de release: é um identificador descritivo, enquanto `GIT_REVISION` é a âncora imutável.

## Gate de regressão

Em pull requests, o CI exige que `base_sha` em `.github/pytest-regression-baseline.json` seja exatamente `github.event.pull_request.base.sha`. Ele cria um worktree e um ambiente isolados no commit base, instala os pacotes registrados no lock desse commit, coleta os node IDs de falhas e erros e exige igualdade exata com o JSON antes de comparar o head. Como o lock do base revisado tem somente o content hash do Poetry desatualizado, o gate recalcula esse metadado apenas na cópia temporária; as versões travadas não são alteradas.

Em `push` e `workflow_call`, o gate valida o SHA do baseline, sua existência e ancestralidade em relação ao commit testado, e compara o head com os mesmos node IDs e classificações. A publicação passa explicitamente o SHA resolvido da tag ao workflow reutilizável, portanto não depende de contexto de pull request e não pula o gate.

## Publicação e rollback

Crie uma tag de release no formato `backend-v<major>.<minor>.<patch>` (por exemplo, `backend-v1.0.0`) em um commit que já pertença a `chore/fast-api` e envie a tag ao GitHub. O workflow valida a ancestralidade, executa testes, verificação do lock e smoke tests do container antes de conceder `packages: write` ao job de publicação. Ele publica `ghcr.io/raydevkit/kerykeion-kabalah:sha-<SHA completo>` e `ghcr.io/raydevkit/kerykeion-kabalah:<tag-da-release>`; nunca publica `latest` e não faz deploy.

Esse gatilho por tag funciona mesmo enquanto `master` continuar sendo a branch padrão, porque o workflow é lido do commit marcado. Não há dispatch manual: o GitHub só disponibilizaria essa opção depois que o workflow existisse na branch padrão.

Após a publicação, obtenha o digest no GHCR e fixe a VPS em `ghcr.io/raydevkit/kerykeion-kabalah@sha256:<digest>`. Para rollback, restaure o digest anterior e recrie somente o container da API.
