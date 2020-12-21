#!/usr/bin/env python3
import argparse
import bibtexparser

example = """Example:

 python3 extract_by_keyword.py -i web/db.bib -o convey.bib -k DFG-CONVEY"""

parser = argparse.ArgumentParser(
    description="Extract bibtex entries by keyword",
    epilog=example,
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
parser.add_argument("-i", "--infile", type=str)
parser.add_argument("-o", "--outfile", type=str)
parser.add_argument("-k", "--keyword", type=str)

if __name__ == "__main__":
    args = parser.parse_args()
    with open(args.infile) as bibtex_file:
        bibtex_database = bibtexparser.load(bibtex_file)
    filtered = []
    writer = bibtexparser.bwriter.BibTexWriter()
    writer.contents = ["entries"]
    writer.indent = "  "
    for entry in bibtex_database.entries:
        if "keyword" in entry and args.keyword in entry["keyword"]:
            filtered.append(entry)
    bibtex_database.entries = filtered
    bibtex_str = bibtexparser.dumps(bibtex_database, writer)
    open(args.outfile, "w").write(bibtex_str)
    print(
        f"Exported {len(filtered)} bibtex entries "
        + f"matching the keyword {args.keyword} "
        + f"from {args.infile} "
        + f"into {args.outfile}!"
    )
