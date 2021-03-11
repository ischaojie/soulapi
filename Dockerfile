FROM python:3.8

ENV PIP_DISABLE_PIP_VERSION_CHECK=on

RUN pip install poetry -i https://mirrors.aliyun.com/pypi/simple/

WORKDIR /app
COPY poetry.lock pyproject.toml /app/

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY . /app

CMD python manage.py db create
CMD python manage.py createsuperuser --noinput
CMD python manage.py run --host 0.0.0.0 --port 8000