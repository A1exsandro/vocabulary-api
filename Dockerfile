# Usar uma imagem base do Python
FROM python:3.11-slim

# Instalar locale e timezone
RUN apt-get update && apt-get install -y \
    locales \
    tzdata \
 && sed -i '/pt_BR.UTF-8/s/^# //g' /etc/locale.gen \
 && locale-gen pt_BR.UTF-8 \
 && apt-get clean

# Configurar locale
ENV LANG=pt_BR.UTF-8 \
    LANGUAGE=pt_BR:pt \
    LC_ALL=pt_BR.UTF-8

# 🔥 Configurar timezone
ENV TZ=America/Cuiaba

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]