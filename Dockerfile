FROM ubuntu:26.04

# hadolint ignore=DL3008
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates \
        fontforge-nox \
        fonttools \
        pipx \
        python3 \
        shellcheck \
        shfmt \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN xargs -a /tmp/requirements.txt pipx install --global

WORKDIR /work
