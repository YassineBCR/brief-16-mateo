FROM python:3.11-alpine

WORKDIR /app

COPY . .

RUN apk add --no-cache postgresql-dev \
    && apk add --no-cache --virtual .build-deps gcc musl-dev \
    &&pip install --upgrade pip && pip install -r requirements.txt


EXPOSE 5432

CMD ["python", "main.py"]