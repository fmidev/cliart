FROM python:3 AS builder

WORKDIR /build

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY . .

RUN pip install --no-cache-dir .

FROM python:3-slim

COPY --from=builder /venv /venv

ENV PYART_QUIET=1

ENTRYPOINT ["/venv/bin/vaimennuskorjain"]
