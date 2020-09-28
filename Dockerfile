FROM python:3.7-stretch
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir /app

ADD ./requirements.txt /app/requirements.txt

COPY . /app
WORKDIR /app

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "Blog.wsgi:application"]