FROM python:3.11.14-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends curl build-essential && rm -rf /var/lib/apt/lists
COPY poetry.lock pyproject.toml README.md /build/
RUN pip install --upgrade pip && pip install poetry==1.4.0
#RUN pip install poetry==1.4.0 && poetry install --no-root
# no usage of poetry in container - build the wheel using pip 
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes 
RUN pip wheel --wheel-dir /wheels -r requirements.txt
COPY . /build
RUN pip wheel --no-deps --wheel-dir /wheels .

FROM python:3.11.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000 WEB_CONCURRENCY=2

WORKDIR /app

RUN groupadd --system app && useradd --system --gid app --create-home --home-dir /home/app app && mkdir -p /app && chown app:app /app
# initialize and assign required directories for the process to the current user (not a root user)
RUN mkdir /app/logs && chown app:app /app/logs && mkdir /app/static && chown app:app /app/static

#copy the wheel files built in the first image:
COPY --from=builder /wheels /wheels
COPY src/app/config.json /app
RUN pip install --no-index --find-links=/wheels /wheels/*.whl && rm -rf /wheels/wheels/*.whl

# note that below instruction creates a default log directory.

USER app
EXPOSE 8000
CMD ["uvicorn", "src.app.main_app:app", "--host", "0.0.0.0", "--port", "8000"]