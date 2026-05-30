#!/bin/sh

for name in Neanes NeanesRTL NeanesStathisSeries; do
	fontforge -script ../scripts/generate-font.py ../sources/${name}.sfd ../fonts/${name}.otf
	fontforge -script ../scripts/generate-font-metadata.py ../sources/${name}.sfd ../metadata/glyphnames.json
done

python ../scripts/generate-contextual-positioning.py ../fonts/*.otf

cp ./*.metadata.json ../fonts
if [ -d ../../neanes/src/assets/fonts ] && [ -w ../../neanes/src/assets/fonts ]; then
	cp ./*.metadata.json ../../neanes/src/assets/fonts
fi
rm ./*.metadata.json

cp ../fonts/Neanes.otf ../docs/_media
if [ -d ../../neanes/docs/.vitepress/theme/assets/fonts ] && [ -w ../../neanes/docs/.vitepress/theme/assets/fonts ]; then
	cp ../fonts/Neanes.otf ../../neanes/docs/.vitepress/theme/assets/fonts
fi
if [ -d ../../neanes/src/assets/fonts ] && [ -w ../../neanes/src/assets/fonts ]; then
	cp ../fonts/*.otf ../../neanes/src/assets/fonts
fi
