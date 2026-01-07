FROM python:3.11.14-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl build-essential && rm -rf /var/lib/apt/lists
RUN curl -ssl https://install.python-poetry.org | python3 

COPY poetry.lock pyproject.toml README.md ./
RUN mkdir /src
COPY src/ /src 
RUN pip install --upgrade pip
RUN pip install poetry==1.4.0 && poetry install --no-root
RUN pip install -e .


EXPOSE 8000
CMD ["uvicorn", "src.app.main_app:app", "--host", "0.0.0.0", "--port", "8000"]