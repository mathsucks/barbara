ARG PYTHON_VERSION="3.13"
ARG POETRY_VERSION="1.8.3"

FROM python:${PYTHON_VERSION}-slim AS builder

ARG POETRY_VERSION
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_NO_INTERACTION=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /src
COPY pyproject.toml poetry.lock README.rst ./
COPY barbara ./barbara
RUN poetry build --format wheel


FROM python:${PYTHON_VERSION}-slim

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# git is required by the @@GIT_COMMIT@@ template variable.
RUN apt-get update \
    && apt-get install --no-install-recommends --yes git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /src/dist/*.whl /tmp/
RUN pip install /tmp/*.whl && rm -f /tmp/*.whl

# Mount the project whose env-file you want to generate here.
WORKDIR /opt/barbara

ENTRYPOINT ["barb"]
