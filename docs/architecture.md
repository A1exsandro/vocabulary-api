# Arquitetura

## Visão geral

O projeto segue uma organização modular por domínio, com separação entre entrada HTTP, regra de negócio, persistência e integrações externas.

Hoje a organização principal está dividida em:

- `application`: casos de uso;
- `application/ports`: contratos de integração;
- `modules`: contratos HTTP, modelos e persistência;
- `core`: configuração e erros compartilhados;
- `infrastructure`: adaptadores concretos;
- `integrations` e `services`: implementações reutilizadas pelos adaptadores.

Cada módulo mantém seus próprios arquivos de:

- `Model`
- `Schema`
- `Repository`
- `Router`

Essa estrutura é simples, prática e adequada para o tamanho atual do projeto.

## Camadas

### Router

Responsável por:

- declarar rotas;
- receber parâmetros e payloads;
- injetar dependências;
- delegar para os use cases.

Arquivos:

- `app/modules/category/category_router.py`
- `app/modules/word/word_router.py`
### Application / Use Cases

Responsável por:

- representar cada ação do sistema explicitamente;
- coordenar repositories e integrações externas;
- controlar commit e rollback;
- aplicar regras de negócio.

Arquivos:

- `app/application/category/use_cases/*`
- `app/application/word/use_cases/*`

### Application / Ports

Responsável por:

- definir interfaces para dependências externas;
- impedir que a camada de aplicação dependa diretamente de OpenRouter, gTTS, Pixabay ou S3.

Arquivos:

- `app/application/ports/vocabulary_enricher.py`
- `app/application/ports/audio_generator.py`
- `app/application/ports/image_generator.py`

### Repository

Responsável por:

- encapsular acesso ao banco;
- executar consultas;
- criar, atualizar, remover e vincular entidades.

Arquivos:

- `app/modules/category/CategoryRepositoy.py`
- `app/modules/word/WordRepositoy.py`

### Schema

Responsável por:

- definir contratos de entrada e saída da API;
- reduzir acoplamento entre request HTTP e model persistido.

Arquivos:

- `app/modules/category/CategorySchema.py`
- `app/modules/word/WordSchema.py`

### Model

Responsável por:

- representar as tabelas do banco;
- descrever relacionamentos entre entidades.

Arquivos:

- `app/modules/category/CategoryModel.py`
- `app/modules/word/WordModel.py`

## Componentes globais

### Banco

`app/core/config.py` concentra:

- inicialização do engine assíncrono;
- criação da sessão assíncrona;
- dependency injection de sessão para FastAPI;
- criação automática das tabelas no startup.

### Exceções de domínio

`app/core/exceptions.py` e `app/core/exception_handlers.py` concentram:

- erros de domínio desacoplados de FastAPI;
- mapeamento desses erros para respostas HTTP.

### Integrações externas

`app/integrations/` contém clientes externos:

- `openrouter_client.py`: normaliza palavra/categoria, traduz e gera frases;
- `pixabay_client.py`: busca imagem associada à palavra;
- `s3_client.py`: upload e geração de URLs para arquivos.

### Services transversais

`app/services/` contém serviços reutilizáveis:

- `audio_service.py`: gera áudio MP3 com gTTS e envia ao storage;
- `image_service.py`: obtém imagem e faz upload ao storage.

### Adaptadores de infraestrutura

`app/infrastructure/adapters/` conecta as portas da aplicação às implementações concretas.

Exemplos:

- `OpenRouterVocabularyEnricher`
- `GttsAudioGenerator`
- `PixabayImageGenerator`

## Modelo de domínio atual

### Category

- `Category`: categoria global única por nome.
- `UserCategory`: vínculo entre usuário e categoria.

### Word

- `Word`: palavra global única por inglês.
- `UserWord`: vínculo entre usuário e palavra.
- `WordCategory`: vínculo entre palavra e categoria.
- `Phrase`: frases relacionadas à palavra.

## Regras importantes de negócio

### Categorias

- categorias são compartilhadas globalmente, mas o acesso é por vínculo com usuário;
- `update` evita alterar uma categoria compartilhada por outros usuários;
- `delete` remove primeiro o vínculo do usuário;
- a categoria só é removida fisicamente quando não restam vínculos de usuário nem palavras relacionadas.

### Palavras

- palavras são compartilhadas globalmente, mas o acesso é por vínculo com usuário;
- na criação, a palavra pode ser normalizada por IA antes de persistir;
- `update` evita alterar uma palavra compartilhada por outros usuários;
- quando necessário, o sistema reaproveita uma palavra existente ou cria uma nova;
- `delete` remove primeiro o vínculo do usuário;
- a palavra só é removida fisicamente quando não há mais usuários vinculados.

## Fluxo técnico de criação de palavra

1. Router recebe o request.
2. Use case consulta o repository para verificar duplicidade.
3. Use case chama OpenRouter para corrigir a palavra, traduzir e gerar frases.
4. Use case chama os adaptadores de `ImageGenerator` e `AudioGenerator`.
5. Repository persiste a palavra.
6. Repository persiste frases e vínculos.
7. A resposta retorna ao cliente.

## Limitações atuais

- os repositories já não fazem `commit`, mas ainda dependem diretamente do SQLModel/SQLAlchemy;
- ainda não existem testes automatizados;
- ainda não há versionamento explícito da API;
- o nome do path `/vocabulary` está inconsistente com o nome do projeto;
- alguns nomes de arquivos têm typo, como `Repositoy`;
- a montagem dos adaptadores ainda está manual, sem container de dependência.

## Próxima evolução recomendada

Se o projeto crescer, a evolução mais consistente é:

1. introduzir casos de uso explícitos por ação;
2. criar interfaces para integrações externas;
3. mover módulos para uma separação ainda mais clara entre domain, application, infrastructure e presentation;
4. adicionar testes unitários e de integração;
5. padronizar responses e tratamento de erro.
