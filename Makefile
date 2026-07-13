UIDGID := $(shell id -u):$(shell id -g)

# Run as the invoking uid/gid so that files written into the bind mount
# are not owned by root.
TOOLCHAIN := docker compose run --rm --user $(UIDGID) toolchain

DOCKERFMT := docker compose run --rm --user $(UIDGID) dockerfmt
HADOLINT := docker compose run --rm -T hadolint

# test reads the fonts that build rewrites, so keep the goals serial even
# under -j.
.NOTPARALLEL:

.PHONY: all image build test lint lint-fix shell

all: lint build test

image:
	docker compose build

# The copies into a sibling neanes checkout happen here, not in build.sh:
# inside the container the sibling path cannot exist, only the host can
# see it.
build: image
	$(TOOLCHAIN) scripts/build.sh
	if [ -d ../neanes/src/assets/fonts ]; then \
		cp fonts/Neanes*.otf fonts/*.metadata.json ../neanes/src/assets/fonts; \
	fi
	if [ -d ../neanes/docs/.vitepress/theme/assets/fonts ]; then \
		cp fonts/Neanes.otf ../neanes/docs/.vitepress/theme/assets/fonts; \
	fi

test: image
	$(TOOLCHAIN) fontbakery check-universal --error-code-on FATAL fonts/*.otf
	$(TOOLCHAIN) fontbakery check-profile tools/fontbakery/sbmufl_profile.py fonts/*.otf

lint: image
	$(TOOLCHAIN) sh -c 'black --check . && isort --check-only . && mypy && shfmt -s -d scripts && shellcheck scripts/*.sh && mbake format --check Makefile'
	$(DOCKERFMT) -c -n Dockerfile
	$(HADOLINT) <Dockerfile

lint-fix: image
	$(TOOLCHAIN) sh -c 'black . && isort . && shfmt -s -w scripts && shellcheck scripts/*.sh && mbake format Makefile'
	$(DOCKERFMT) -w -n Dockerfile

shell: image
	$(TOOLCHAIN) bash