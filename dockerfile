FROM python:3.11.14-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl build-essential && rm -rf /var/lib/apt/lists
RUN curl -ssl https://install.python-poetry.org | python3 

COPY poetry.lock pyproject.toml README.md ./
RUN mkdir /src
COPY src/ /src 
RUN pip install --upgrade pip
RUN pip install poetry==1.4.0 && poetry install --no-root
RUN pip install -e .

# ENV PATH="/root/.local/bin:$PATH"

# COPY pyproject.toml poetry.lock /app/
# note: below avoids having Poetry installed in the container but requires as a deployment step to have a requirements.txt file exported from Poetry
# (per documentation, use poetry export -f requirements.txt --output requirements.txt --without-hashes to export dependencies to a requirements.txt file)
# if generating requirements.txt is not a part of the workflow, this will fail.
# COPY requirements.txt /app/
# RUN pip install -r requirements.txt
# RUN poetry install 

#nota: o que foi feito para corrigir o problema do src.app.bla: da pasta raiz do repo (qr-code-generator, rodar pip install -e . TODO o projeto fica disponível)
#daí, temos que ver como fazer isso no Docker pois pra gente o ideal era só ter a parte de src pra baixo. Se pá pode ser interessante colocar o pyproject.toml dentro de src
# e redirecionar oas instalações pra dentro dali.


EXPOSE 8000
CMD ["uvicorn", "src.app.main_app:app", "--host", "0.0.0.0", "--port", "8000"]