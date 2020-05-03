FROM python:3.7-alpine

ADD pip-requirements.txt /pip-requirements.txt
RUN pip install --no-cache-dir -r /pip-requirements.txt
