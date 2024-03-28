FROM python:3.9

RUN mkdir /mosobl

WORKDIR /mosobl

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY config.yaml /mosobl

COPY configuration.py /mosobl

COPY  src /mosobl/src

CMD gunicorn src.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000