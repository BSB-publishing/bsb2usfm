
all: results/GEN.usfm interlinear/01GENBSB_int.usfm

results/GEN.usfm : bsb2usfm.py data/bsb_tables.csv
	- ./bsb2usfm.py -o results/%.usfm -f demo_data/sample_footnotes.tsv -n demo_data/sample_book_names.xml data/bsb_tables.csv

interlinear/01GENBSB_int.usfm: bsb2usfm.py data/bsb_tables.csv
	- ./bsb2usfm.py -I -o results/^%BSB_int.usfm -f demo_data/sample_footnotes.tsv -n demo_data/sample_book_names.xml data/bsb_tables.csv
