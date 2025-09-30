# syntax=docker/dockerfile:1

# Frontend build stage
FROM docker.io/library/node:20-alpine AS frontend
WORKDIR /build
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
COPY templates/ ../templates/
RUN npm run build

# Python application stage
FROM docker.io/library/python:3.12-alpine

# Application configuration
ENV DATA_DIR=/config \
	STUDENT_CSV_PATH=/config/students.csv \
	FLASK_APP=wsgi:app

USER root

COPY . /app
COPY --from=frontend /static/dist /app/static/dist

WORKDIR /app

RUN \
	pip3 install --no-cache-dir -r \
		requirements.txt \
	&& \
	mkdir -p \
        /config \
	&& \
	chown nobody:nogroup \
        /config \
        /app \
	&& \
	rm -rf /tmp/*


USER nobody:nogroup

VOLUME ["/config"]
EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--access-logfile", "-", "--preload", "wsgi:app"]
