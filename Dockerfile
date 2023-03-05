FROM tiangolo/meinheld-gunicorn-flask:python3.8

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./app.py /app/main.py
COPY ./config.json /app/config.json