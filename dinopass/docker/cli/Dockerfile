FROM python:latest

RUN apt-get update -y
RUN apt-get upgrade -y

ENV PYTHONPATH=/code
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code/db
COPY backend/db/dinopass.db .

WORKDIR /code/backend

COPY backend/requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY backend .

ENTRYPOINT ["tail", "-f", "/dev/null"]