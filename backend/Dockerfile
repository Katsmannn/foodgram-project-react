FROM python:3.7-slim

WORKDIR /foodgram

COPY backend/foodgram/requirements.txt .

RUN pip3 install -r ./requirements.txt --no-cache-dir

COPY . .

WORKDIR foodgram_api/

CMD ["gunicorn", "foodgram_api.wsgi:application", "--bind", "0:8000"]
