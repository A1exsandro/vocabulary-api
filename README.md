# vocabulary-api

# Start
- uvicorn app.main:app --host=localhost --port=8888 --reload
- uvicorn app.main:app --host=0.0.0.0 --port=8888 --reload

# Criar e ativar ambiente Virtual Windows
* python -m venv .venv
* .venv\Scripts\activate

# Criar e ativar ambiente Virtual Linux
* python3 -m venv .venv
* . .venv/bin/activate

# Instalar dependências
* pip install -r requirements.txt

* pip freeze > requirements.txt

# Build
docker build -t registry.nst.art.br/vocabulary-api:0.0.2 -f Dockerfile .
docker push registry.nst.art.br/vocabulary-api:0.0.2
