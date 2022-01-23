FROM python:3.7-slim

WORKDIR /foodgram/foodgram_api/

COPY backend/foodgram/requirements.txt ../

RUN pip3 install -r ../requirements.txt --no-cache-dir

COPY backend/foodgram/ ../

CMD ["gunicorn", "foodgram_api.wsgi:application", "--bind", "0:8000"]
