FROM python:3.10

RUN mkdir build

WORKDIR /build


# Install poetry and project deps
COPY . .
ENV POETRY_HOME=/poetry
ENV PATH=$POETRY_HOME/bin:$PATH
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN poetry install

EXPOSE 8000

CMD poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000