FROM python:3.13.0-alpine3.20

WORKDIR /app
COPY .python-version ./
COPY pyproject.toml ./
COPY requirements.lock ./

# FIXME: Failing step
RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir -r requirements.lock

COPY src .