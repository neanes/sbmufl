#!/bin/sh

set -e

SCRIPT_DIR=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)

# The generator scripts import sibling modules (e.g.
# generate_collision_regions) via the working directory, since
# `fontforge -script` does not put the script's directory on sys.path.
cd -- "$SCRIPT_DIR"

# Pin the timestamps FontForge embeds in generated fonts (head table) and
# saved SFDs (ModificationTime) so that rebuilds are byte-identical.
# 1646795337 matches the CreationTime stored in the source SFDs.
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-1781842028}"

for name in Neanes NeanesRTL NeanesStathisSeries; do
	engraving_name="${name}Engraving"

	# Normal font
	fontforge -script generate-font.py \
		../sources/${name}.sfd \
		../fonts/${name}.otf

	# Normal metadata
	fontforge -script generate-font-metadata.py \
		../sources/${name}.sfd \
		../metadata/glyphnames.json

	# Zero-space engraving font + metadata
	fontforge -script generate-font-zero-space.py \
		../sources/${name}.sfd \
		../fonts/${engraving_name}.otf \
		../sources/${engraving_name}.sfd \
		../metadata/glyphnames.json

	fontforge -script generate-font-metadata.py \
		../sources/${engraving_name}.sfd \
		../metadata/glyphnames.json
done

mv ./*.metadata.json ../fonts

cp ../fonts/Neanes.otf ../docs/_media
