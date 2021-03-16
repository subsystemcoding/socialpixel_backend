# SocialPixel Backend

FROM python:3

LABEL maintainer="bjr5@hw.ac.uk"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt clean && apt update
RUN apt install -y libpq-dev python3-dev

RUN mkdir /socialpixel_backend

WORKDIR /socialpixel_backend

ADD . /socialpixel_backend/

RUN pip install -r requirements.txt

EXPOSE 8000

CMD python manage.py migrate && python manage.py runserver 0.0.0.0:8000
