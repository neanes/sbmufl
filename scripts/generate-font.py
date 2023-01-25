import fontforge

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(
            "USAGE: ffpython generate-font-metadata.py <relative/path/to/font.sfd> [relative/path/to/font.otf]")
        exit(1)

    infile = sys.argv[1]
    outfile = sys.argv[2]

    font = fontforge.open(infile)

    font.generate(outfile)
