# API Reference

## Base URL

```text
/api/vocabulary
```

## Convenções

- `user_id` identifica o dono do vínculo com categoria ou palavra.
- `category_id` e `word_id` são UUIDs.
- os endpoints de `delete` recebem `user_id` no corpo para validar o escopo do usuário.

## Category

### Criar categoria

`POST /api/vocabulary/category`

Request:

```json
{
  "name": "animals",
  "user_id": "user-123"
}
```

Response:

```json
{
  "detail": "Categoria Criada com sucesso!"
}
```

### Listar categorias do usuário

`GET /api/vocabulary/category/categories_by_user?user_id=user-123`

Response:

```json
[
  {
    "id": "f1ef52ef-8d3f-4c4a-8ae0-5f5d59598364",
    "name": "animals"
  }
]
```

### Atualizar categoria

`PUT /api/vocabulary/category/{category_id}`

Request:

```json
{
  "name": "food",
  "user_id": "user-123"
}
```

Response:

```json
{
  "detail": "Categoria atualizada com sucesso!"
}
```

### Remover categoria

`DELETE /api/vocabulary/category/{category_id}`

Request:

```json
{
  "user_id": "user-123"
}
```

Response:

```json
{
  "detail": "Categoria removida com sucesso."
}
```

## Word

### Criar palavra

`POST /api/vocabulary/word`

Request:

```json
{
  "english": "apple",
  "user_id": "user-123",
  "category_id": "f1ef52ef-8d3f-4c4a-8ae0-5f5d59598364"
}
```

Response esperada:

- quando a palavra é nova, retorna o objeto persistido;
- quando a palavra já existe para o usuário, retorna:

```json
{
  "detail": "Essa palavra já está na sua lista."
}
```

### Listar palavras do usuário por categoria

`GET /api/vocabulary/word/words?user_id=user-123&category_id=f1ef52ef-8d3f-4c4a-8ae0-5f5d59598364`

Response:

```json
[
  {
    "userId": "user-123",
    "english": "apple",
    "portuguese": "maçã",
    "phrases": [
      {
        "id": "f0f7ce79-ec6f-4f87-b410-bf30f7d387e8",
        "text": "This is an apple.",
        "audioUrl": "https://..."
      }
    ],
    "audioUrl": "https://...",
    "imageUrl": "https://..."
  }
]
```

### Atualizar palavra

`PUT /api/vocabulary/word/{word_id}`

Request:

```json
{
  "english": "banana",
  "user_id": "user-123",
  "category_id": "f1ef52ef-8d3f-4c4a-8ae0-5f5d59598364"
}
```

Response:

```json
{
  "detail": "Palavra atualizada com sucesso."
}
```

### Remover palavra

`DELETE /api/vocabulary/word/{word_id}`

Request:

```json
{
  "user_id": "user-123"
}
```

Response:

```json
{
  "detail": "Palavra removida com sucesso."
}
```

## Códigos de erro esperados

### 404

Usado quando:

- categoria não existe;
- palavra não existe;
- o vínculo não pertence ao usuário informado.

### 409

Usado quando:

- a categoria já está vinculada ao usuário;
- a palavra já está vinculada ao usuário.

## Dependências externas que impactam a API

### OpenRouter

Usado para:

- validar ou corrigir palavras;
- validar ou corrigir categorias;
- traduzir para português;
- gerar frases simples.

### Pixabay

Usado para:

- buscar imagem ilustrativa da palavra.

### MinIO / S3

Usado para:

- armazenar imagens;
- armazenar áudios;
- servir URLs pré-assinadas.

### gTTS

Usado para:

- gerar áudio MP3 da palavra;
- gerar áudio MP3 das frases.

## Melhor fonte para teste manual

Depois de subir a API, use:

- `/docs`
- `/redoc`

Essas interfaces mostram os schemas reais gerados pelo FastAPI e são a referência operacional mais precisa para validar requests e responses.
