# Event-Horizon API server


API for Event-Horizon using FastAPI


## Prerequisites for local development


The program expects to find a `.env` file in the project root with the following variables:

```
ENVIRONMENT=<development|production>
SUPERUSER_USERNAME=<any@valid.email>
SUPERUSER_PASSWORD=<password of your choice>
```


### Install poetry and project dependencies


```bash
python3.10 -m pip install poetry
poetry install
```


Running `poetry run COMMAND` will run any COMMAND in a shell environment with the proper python version and project dependencies available on $PATH. `poetry shell` will drop you into that shell environment. Within VSCode, you can set the proper python interpreter and the integrated terminal should be in the proper environment  automagically (see bellow) in which case the `poetry run` prefix is unecessary.


### VSCode Setup


VSCode should detect poetry and ask you if you would like to use is as the project python interpreter. If it doesn't, or if you run into related issues, get the poetry python path via `poetry run which python` and copy it to `.vscode/settings.json`. Your settings should look something like so:


```json
# .vscode/settings.json
{
    "python.defaultInterpreterPath": "<your $HOME>/.cache/pypoetry/virtualenvs/event-horizon-api-b5xDj491-py3.10/bin/python",
}
```


## Usage


### Locally


```bash
uvicorn app.main:app --reload
```

### Docker


```bash
docker build -t event-horizon-api:local .
docker run -it --rm -p 8000:8000 event-horizon-api:local
```


In both cases the OpenAPI spec will be viewable at [http://localhost:8000/docs](http://localhost:8000/docs)


### Auth (dev)


user: cb@qc.croixbleue.ca

password: password

## Tests


```bash
pytest
```


