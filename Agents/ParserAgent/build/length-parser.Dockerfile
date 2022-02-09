FROM python:3.10.2-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ECS_AVAILABLE_LOGGING_DRIVERS='["json-file","awslogs"]'

ENV RDS_HOSTNAME=$RDS_HOSTNAME
ENV RDS_PORT=$RDS_PORT
ENV RDS_DB_NAME=$RDS_DB_NAME
ENV RDS_USERNAME=$PARSERAGENT_RDS_USERNAME
ENV RDS_PASSWORD=$PARSERAGENT_RDS_PASSWORD

COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

RUN useradd appuser && chown -R appuser /app
USER appuser

CMD ["python", "LengthParser.py"]