FROM python:3.8
WORKDIR /opt/barbara
COPY . .
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry build && \
    pip install dist/barbara* && \
    pip uninstall --yes poetry
ENTRYPOINT ["barb"]
