for name in Neanes NeanesRTL NeanesStathisSeries; do
    fontforge -script ../scripts/generate-font.py ../sources/${name}.sfd ../fonts/${name}.otf
    fontforge -script ../scripts/generate-font-metadata.py ../sources/${name}.sfd ../metadata/glyphnames.json
done

cp *.metadata.json ../fonts
cp *.metadata.json ../../neanes/src/assets/fonts
rm *.metadata.json

cp ../fonts/Neanes.otf ../docs/_media
cp ../fonts/Neanes.otf ../../neanes/docs/.vitepress/theme/assets/fonts
cp ../fonts/*.otf ../../neanes/src/assets/fonts

