#!/usr/bin/python3

import argparse, csv
import usfmtc

parser = argparse.ArgumentParser()
parser.add_argument("infile",nargs="+",help="Input usfm file")
parser.add_argument("-o","--outfile",help="Ouput txt file")
args = parser.parse_args()

results = []
for infile in args.infile:
    doc = usfmtc.readFile(infile)
    doc.addorncv()
    for e, isin in doc.iterusx():
        if not isin or e.tag != "note":
            continue
        ref = e.pos.ref
        types = []
        for c in e:
            s = c.get("style", "")
            if s in ("fq", "fqa"):
                types.append(s)
        if len(types):
            results.append([ref] + types)

if args.outfile:
    with open(args.outfile, "w", encoding="utf-8") as outf:
        wrtr = csv.writer(outf, delimiter="\t")
        wrtr.writerow(["ref", "mrkrs"])
        wrtr.writerows(results)
