#!/bin/sh

set -e

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

VENV_DIR="$REPO_ROOT/.venv"
REQUIREMENTS="$REPO_ROOT/requirements.txt"

if [ -z "$CI" ]; then
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment at $VENV_DIR"
        python3 -m venv "$VENV_DIR"
    fi

    . "$VENV_DIR/bin/activate"

    python -m pip install -q -r "$REQUIREMENTS"
fi

for name in Neanes NeanesRTL NeanesStathisSeries; do
    engraving_name="${name}Engraving"
    engraving_metadata_name=$(printf '%s' "$engraving_name" | tr '[:upper:]' '[:lower:]')

    # Normal font
    fontforge -script ../scripts/generate-font.py \
        ../sources/${name}.sfd \
        ../fonts/${name}.otf

    # Normal metadata
    fontforge -script ../scripts/generate-font-metadata.py \
        ../sources/${name}.sfd \
        ../metadata/glyphnames.json

    # Zero-space engraving font + metadata
    fontforge -script ../scripts/generate-font-zero-space.py \
        ../sources/${name}.sfd \
        ../fonts/${engraving_name}.otf \
        ../sources/${engraving_name}.sfd \
        ../metadata/glyphnames.json

    fontforge -script ../scripts/generate-font-metadata.py \
        ../sources/${engraving_name}.sfd \
        ../metadata/glyphnames.json
done

cp ./*.metadata.json ../fonts

if [ -d ../../neanes/src/assets/fonts ]; then
    cp ../fonts/Neanes*.otf ../../neanes/src/assets/fonts
    cp ./*.metadata.json ../../neanes/src/assets/fonts
fi

rm ./*.metadata.json

cp ../fonts/Neanes.otf ../docs/_media

if [ -d ../../neanes/docs/.vitepress/theme/assets/fonts ]; then
    cp ../fonts/Neanes.otf ../../neanes/docs/.vitepress/theme/assets/fonts
fi