FROM python:3.10

ENV PYTHONUNBUFFERED 1

RUN mkdir rhms
WORKDIR /rhms

COPY requirements.txt /rhms/

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /rhms/

RUN sh init.sh

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]