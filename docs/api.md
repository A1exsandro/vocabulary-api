# API Reference

## Base URL

```text
/api/vocabulary
```

## Convenções

- `user_id` identifica o dono do vínculo com categoria ou palavra.
- `category_id` e `word_id` são UUIDs.
- endpoints de `delete` recebem `user_id` no corpo para validar escopo.

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

### Atualizar categoria

`PUT /api/vocabulary/category/{category_id}`

### Remover categoria

`DELETE /api/vocabulary/category/{category_id}`

## Word

### Criar palavra com IA

`POST /api/vocabulary/word`

Request:

```json
{
  "english": "apple",
  "user_id": "user-123",
  "category_id": "f1ef52ef-8d3f-4c4a-8ae0-5f5d59598364"
}
```

### Importar palavras em lote (JSON)

`POST /api/vocabulary/word/import`

Request:

```json
{
  "schema_version": "1.0",
  "user_id": "user-123",
  "category_id": "f1ef52ef-8d3f-4c4a-8ae0-5f5d59598364",
  "mode": "skip",
  "items": [
    {
      "english": "apple",
      "portuguese": "maçã",
      "sentences": [
        { "english": "This is an apple.", "portuguese": "Isto é uma maçã." },
        { "english": "I eat an apple every day.", "portuguese": "Eu como uma maçã todos os dias." }
      ]
    }
  ]
}
```

Response:

```json
{
  "total": 1,
  "created": 1,
  "linked": 0,
  "updated": 0,
  "skipped": 0,
  "failed": 0,
  "errors": []
}
```

### Importar palavras por arquivo

`POST /api/vocabulary/word/import/file`

`multipart/form-data`:

- `file`: `.json`, `.md` ou `.markdown`
- `user_id` (opcional, sobrescreve valor do arquivo)
- `category_id` (opcional, sobrescreve valor do arquivo)
- `mode` (opcional: `skip`, `update`, `error`)

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
        "translation": "Isto é uma maçã.",
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

### Remover palavra

`DELETE /api/vocabulary/word/{word_id}`

## Códigos de erro esperados

### 404

- categoria não existe;
- palavra não existe;
- vínculo não pertence ao usuário.

### 409

- categoria já vinculada ao usuário;
- palavra já vinculada ao usuário.

## Melhor fonte para teste manual

Depois de subir a API, use:

- `/docs`
- `/redoc`
