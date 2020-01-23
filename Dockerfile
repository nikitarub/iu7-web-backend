FROM python:3.7

WORKDIR /tmp

COPY . .

RUN pip install -r requirements.txt
RUN cd lobster_backend/ && python manage.py migrate
