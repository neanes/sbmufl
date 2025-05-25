fontforge -script ../scripts/generate-font.py ../sources/Neanes.sfd ../fonts/Neanes.otf
fontforge -script ../scripts/generate-font-metadata.py ../sources/Neanes.sfd ../metadata/glyphnames.json

fontforge -script ../scripts/generate-font.py ../sources/NeanesRTL.sfd ../fonts/NeanesRTL.otf
fontforge -script ../scripts/generate-font-metadata.py ../sources/NeanesRTL.sfd ../metadata/glyphnames.json

cp *.metadata.json ../fonts
cp *.metadata.json ../../neanes/src/assets/fonts
rm *.metadata.json

cp ../fonts/Neanes.otf ../docs/_media
cp ../fonts/Neanes.otf ../../neanes/docs/.vitepress/theme/assets/fonts
cp ../fonts/*.otf ../../neanes/src/assets/fonts

