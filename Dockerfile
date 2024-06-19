FROM python:3.12.4-alpine3.20
COPY automation .
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ENV PATH="/:${PATH}"