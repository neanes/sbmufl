#!/bin/sh

set -e

ZERO_SPACE_DIR="$(mktemp -d)"
trap 'rm -rf "$ZERO_SPACE_DIR"' EXIT

for name in Neanes NeanesRTL NeanesStathisSeries; do
	fontforge -script ../scripts/generate-font.py ../sources/${name}.sfd ../fonts/${name}.otf
	fontforge -script ../scripts/generate-font-metadata.py ../sources/${name}.sfd ../metadata/glyphnames.json
done

cp ./*.metadata.json ../fonts

if [ -d ../../neanes/src/assets/fonts ]; then
	cp ./*.metadata.json ../../neanes/src/assets/fonts

	for name in Neanes NeanesRTL NeanesStathisSeries; do
		fontforge -script ../scripts/generate-font-zero-space.py \
			../sources/${name}.sfd \
			"$ZERO_SPACE_DIR/${name}.otf" \
			/dev/null \
			../metadata/glyphnames.json
	done

	cp "$ZERO_SPACE_DIR"/*.otf ../../neanes/src/assets/fonts
fi

rm ./*.metadata.json

cp ../fonts/Neanes.otf ../docs/_media

if [ -d ../../neanes/docs/.vitepress/theme/assets/fonts ]; then
	cp ../fonts/Neanes.otf ../../neanes/docs/.vitepress/theme/assets/fonts
fi