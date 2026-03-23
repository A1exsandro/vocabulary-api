# Vocabulary API

API backend para gerenciamento de vocabulário em inglês por usuário, com geração assistida de tradução, frases, áudio e imagem.

## O que o projeto faz

Esta API permite:

- criar categorias de estudo por usuário;
- criar palavras em inglês vinculadas a categorias;
- gerar tradução em português e frases simples com IA;
- gerar áudio das palavras e frases;
- buscar imagem ilustrativa para a palavra;
- armazenar metadados no banco e arquivos em storage compatível com S3.

## Stack

- Python 3.11
- FastAPI
- SQLModel / SQLAlchemy Async
- PostgreSQL
- MinIO / S3
- OpenRouter
- Pixabay
- gTTS
- Docker / Docker Compose

## Como a aplicação está organizada

```text
app/
  application/
    category/use_cases/    # Casos de uso de category
    word/use_cases/        # Casos de uso de word
    ports/                 # Interfaces da camada de aplicação
  core/
    config.py              # Banco, sessão e dependências globais
    exceptions.py          # Exceções de domínio
    exception_handlers.py  # Tradução de erros para HTTP
  integrations/
    openrouter_client.py   # Geração de tradução e frases com IA
    pixabay_client.py      # Busca de imagem
    s3_client.py           # Upload e URLs do storage
  infrastructure/
    adapters/             # Implementações concretas das portas
  services/
    audio_service.py       # Geração de áudio com gTTS
    image_service.py       # Geração e upload de imagem
  modules/
    category/
      CategoryModel.py
      CategorySchema.py
      CategoryRepositoy.py
      category_router.py
    word/
      WordModel.py
      WordSchema.py
      WordRepositoy.py
      word_router.py
  main.py
```

## Arquitetura usada

O projeto está organizado em camadas por módulo:

- `router`: expõe os endpoints HTTP;
- `application/use_cases`: concentra os casos de uso;
- `application/ports`: define contratos para dependências externas;
- `repository`: encapsula acesso a dados;
- `schema`: contratos de entrada e saída;
- `model`: entidades persistidas no banco.

Os `repositories` não controlam mais transação. A confirmação da transação acontece na camada de caso de uso, o que aproxima o projeto de uma arquitetura limpa.
Os `use cases` também não dependem mais diretamente das integrações concretas; eles dependem de portas, implementadas hoje em `infrastructure/adapters`.

## Fluxo principal

### Categoria

1. O cliente envia nome da categoria e `user_id`.
2. A API verifica se a categoria já existe.
3. Se necessário, o nome é normalizado via OpenRouter.
4. A categoria é criada e vinculada ao usuário.

### Palavra

1. O cliente envia palavra em inglês, `user_id` e `category_id`.
2. A API valida/corrige a palavra com OpenRouter.
3. Gera tradução para português e 3 frases simples.
4. Gera áudio da palavra e das frases com gTTS.
5. Busca uma imagem relacionada no Pixabay.
6. Faz upload dos arquivos para S3/MinIO.
7. Salva palavra, frases e vínculos no banco.

## Módulos disponíveis

- `category`: create, read, update e delete.
- `word`: create, read, update e delete.

## Endpoints

Base path:

```text
/api/vocabulary
```

### Category

- `POST /category`
- `PUT /category/{category_id}`
- `DELETE /category/{category_id}`
- `GET /category/categories_by_user?user_id=...`

### Word

- `POST /word`
- `PUT /word/{word_id}`
- `DELETE /word/{word_id}`
- `GET /word/words?user_id=...&category_id=...`

Documentação detalhada dos endpoints:

- [API Reference](./docs/api.md)

## Configuração de ambiente

Crie um arquivo `.env` com base em `.env.example`.

Principais variáveis:

- `DATABASE_URL`: conexão assíncrona com PostgreSQL
- `S3_ENDPOINT`: endpoint interno do storage
- `S3_PUBLIC_ENDPOINT`: endpoint público para acesso aos arquivos
- `S3_ACCESS_KEY`
- `S3_SECRET_KEY`
- `S3_AUDIO_BUCKET_NAME`
- `S3_IMAGE_BUCKET_NAME`
- `S3_REGION`
- `PIXABAY_API_KEY`
- `OPENROUTER_API_KEY`

## Executando localmente

### 1. Criar e ativar ambiente virtual

Linux:

```bash
python3 -m venv .venv
. .venv/bin/activate
```

Windows:

```bat
python -m venv .venv
.venv\Scripts\activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Subir o banco com Docker Compose

```bash
docker compose -f docker/docker-compose.yml up -d
```

### 4. Rodar a API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload
```

## Docker

Build:

```bash
docker build -t vocabulary-api:local -f Dockerfile .
```

Run:

```bash
docker run --env-file .env -p 8000:8000 vocabulary-api:local
```

## Documentação automática

Como a aplicação usa FastAPI, a documentação OpenAPI já fica disponível ao subir a API:

- `/docs`
- `/redoc`

Essas rotas são a melhor fonte para testar rapidamente os endpoints, enquanto os arquivos em `docs/` servem como documentação técnica do projeto.

## Documentação complementar

- [Arquitetura](./docs/architecture.md)
- [API Reference](./docs/api.md)

## Observações atuais

- o prefixo base da API é `/api/vocabulary`;
- o banco é inicializado no startup da aplicação;
- tabelas são criadas automaticamente com `SQLModel.metadata.create_all`;
- a aplicação depende de serviços externos para a criação completa de palavras.
