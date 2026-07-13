FROM ubuntu:26.04

# hadolint ignore=DL3008
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        fontforge-nox \
        fonttools \
        pipx \
        python3 \
        python3-pip \
        shellcheck \
        shfmt \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt

# fontbakery depends on opentype-sanitizer, which publishes no Linux arm64
# wheels, so build it from source into a local wheelhouse. python3-pip above
# exist only for this). --no-binary forces the same source build on amd64,
# keeping both architectures on one code path. The sdist needs two fixes to
# build: the sed drops copy_file()'s dry_run argument, which current setuptools'
# distutils no longer accepts, and the forced <cstdint> include supplies the
# uint*_t declarations that the bundled ots sources are missing under GCC 13+.
RUN set -eu; \
    ots_version="$(sed -n 's/^opentype-sanitizer==//p' /tmp/requirements.txt)"; \
    test -n "${ots_version}"; \
    python3 -m pip download --no-deps --no-binary=opentype-sanitizer --dest /tmp "opentype-sanitizer==${ots_version}" \
    && mkdir -p /tmp/opentype-sanitizer \
    && tar -xf "/tmp/opentype_sanitizer-${ots_version}.tar.gz" -C /tmp/opentype-sanitizer --strip-components=1 \
    && sed -i 's|copy_file(exe_fullpath, dest_path, verbose=self.verbose, dry_run=self.dry_run)|copy_file(exe_fullpath, dest_path, verbose=self.verbose)|' /tmp/opentype-sanitizer/setup.py \
    && CXXFLAGS="-include cstdint" python3 -m pip wheel --wheel-dir /tmp/wheelhouse /tmp/opentype-sanitizer \
    && rm -rf /tmp/opentype-sanitizer "/tmp/opentype_sanitizer-${ots_version}.tar.gz"

# opentype-sanitizer is only needed as a fontbakery dependency, not as a tool of
# its own: drop it from the pipx install and let --find-links satisfy it from
# the wheel built above.
RUN sed '/^opentype-sanitizer==/d' /tmp/requirements.txt >/tmp/pipx-requirements.txt \
    && xargs -a /tmp/pipx-requirements.txt pipx install --global --pip-args="--find-links=/tmp/wheelhouse" \
    && rm -f /tmp/pipx-requirements.txt

WORKDIR /work
