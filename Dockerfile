FROM python:3.7.4-alpine3.10
COPY automation automation
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ENV PATH="/:${PATH}"