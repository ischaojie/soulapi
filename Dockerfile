FROM python:3.7

COPY . /soulapi/
WORKDIR /soulapi

RUN pip install pipenv

# install all requirements in system
RUN pipenv install --system --deploy

CMD python manage.py run --host 0.0.0.0 --port 8000


