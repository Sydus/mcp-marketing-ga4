# syntax=docker/dockerfile:1.7
FROM python:3.12-slim
ARG BUILD_VERSION=dev
ARG MCP_API_KEY=""
ENV BUILD_VERSION=${BUILD_VERSION}
ENV MCP_API_KEY=${MCP_API_KEY}
WORKDIR /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends git openssh-client \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p -m 0700 ~/.ssh \
    && ssh-keyscan github.com >> ~/.ssh/known_hosts
COPY . .
RUN --mount=type=ssh pip install --no-cache-dir .
CMD ["mcp-marketing-ga4"]
