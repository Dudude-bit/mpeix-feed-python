FROM python:3.9

WORKDIR /app

RUN apt update

RUN apt install python3-pip

COPY ./requirements.txt ./

RUN pip3 install -r requirements.txt

COPY ./ ./

CMD uvicorn run app:app --host 0.0.0.0 --port 8000 --workers 4