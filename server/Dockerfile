FROM python:3.12 as build-env

ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app

# Add Pipfiles to image and install them
COPY . /app

RUN apt-get update
RUN apt-get install -y gdal-bin libgdal-dev

# Install Pipenv and run
RUN pip install pipenv --no-cache-dir
RUN pipenv install --system --deploy --ignore-pipfile

# Add Django entrypoint script to docker
COPY ./scripts/entrypoint.sh /entrypoint.sh
RUN chmod u+x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]