import argparse
import fontforge

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate font")
    parser.add_argument("infile", help="Relative path to font.sfd")
    parser.add_argument("outfile", help="Relative path to font.otf")
    args = parser.parse_args()

    font = fontforge.open(args.infile)

    font.generate(args.outfile)
