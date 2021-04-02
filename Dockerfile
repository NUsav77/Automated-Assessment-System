FROM python:3.9 as base
ENV PYTHONUNBUFFERED=1
ENV PIPENV_VENV_IN_PROJECT=true
RUN apt-get update && \
    pip install --no-cache-dir pipenv && \
    mkdir -p /srv/app
WORKDIR /srv/app
COPY . /srv/app
RUN pipenv install
EXPOSE 8000
CMD pipenv run python manage.py runserver --settings AAS.settings.docker 0.0.0.0:8000

