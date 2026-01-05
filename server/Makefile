export PIPENV_VERBOSITY=-1
OS := $(shell uname -s 2>/dev/null || echo not)

.PHONY: setup
setup:
	make migrate
	make superuser
	make run
	
.PHONY: run
run:
	pipenv run python src/manage.py runserver 0.0.0.0:8001

.PHONY: shell
shell:
	pipenv run python src/manage.py shell

.PHONY: superuser
superuser:
	DJANGO_SUPERUSER_PASSWORD=admin pipenv run python src/manage.py createsuperuser --no-input \
		--username admin@admin.com \
		--email admin@admin.com

.PHONY: migrate
migrate: 
	pipenv run python src/manage.py makemigrations
	pipenv run python src/manage.py migrate

.PHONY: clean
clean:
	rm -rf ./src/db.sqlite3
	rm -rf ./src/__pycache__
	rm -rf ./src/shyft/__pycache__

.PHONY: collectstatic
collectstatic:
	pipenv run python src/manage.py collectstatic --no-input

.PHONY: run/gunicorn
run/gunicorn:
	PYTHONPATH=src gunicorn config.wsgi:application --bind 0.0.0.0:8000

.PHONY: docker/build
docker/build:
	docker build -f ./Dockerfile -t acad_ai:latest .

.PHONY: tidy
tidy:
	pipenv run autoflake --in-place --remove-all-unused-imports -r --exclude migrations ./src
	pipenv run isort --atomic ./src/
	pipenv run black ./src/ --exclude=migrations

