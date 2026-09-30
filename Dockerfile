FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.txt .

RUN apt-get update \
	&& apt-get upgrade -y --no-install-recommends \
	&& pip install --no-cache-dir -r requirements.txt \
	&& rm -rf /var/lib/apt/lists/*

COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]