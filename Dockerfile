FROM python:3.7
WORKDIR /soulapi
COPY . .
RUN pip install pipenv
# install all requirements in system
RUN pipenv install --system --deploy
ENV SOUL_API_DATABASE_URI=sqlite:////data/app.db

# init and run
CMD python manage.py db create
CMD python manage.py createsuperuser --noinput
CMD python manage.py run --host 0.0.0.0 --port 8000


