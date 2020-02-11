FROM python:3.8
WORKDIR /opt/barbara
COPY . .
RUN pip install poetry
RUN poetry install
ENTRYPOINT ["poetry", "run", "barb"]
