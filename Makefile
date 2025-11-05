PYTHON=venv/bin/python3

all: results/GEN.usfm results/int/01GENBSB_int.usfm results/strongs/01GENBSB_strongs.usfm results/strongs_full/01GENBSB_full_strongs.usfm results_usj/GEN.usj results_usj/int/01GENBSB_int.usj results_usj/strongs/01GENBSB_strongs.usj results_usj/strongs_full/01GENBSB_full_strongs.usj
	$(PYTHON) create_zips.py

results/GEN.usfm : bsb2usfm.py
	- $(PYTHON) bsb2usfm.py -o results/%.usfm -f demo_data/sample_footnotes.tsv -n demo_data/sample_book_names.xml

results/int/01GENBSB_int.usfm: bsb2usfm.py
	- $(PYTHON) bsb2usfm.py -I -o results/int/^%BSB_int.usfm -f demo_data/sample_footnotes.tsv -n demo_data/sample_book_names.xml

results/strongs/01GENBSB_strongs.usfm: bsb2usfm.py
	$(PYTHON) bsb2usfm.py -S -o results/strongs/^%BSB_strongs.usfm -f demo_data/sample_footnotes.tsv -n demo_data/sample_book_names.xml

results/strongs_full/01GENBSB_full_strongs.usfm: bsb2usfm.py
	$(PYTHON) bsb2usfm.py -S -P -B -o results/strongs_full/^%BSB_full_strongs.usfm -f demo_data/sample_footnotes.tsv -n demo_data/sample_book_names.xml

results_usj/GEN.usj : bsb2usfm.py
	- $(PYTHON) bsb2usfm.py -o results_usj/%.usj -f demo_data/sample_footnotes.tsv -n demo_data/sample_book_names.xml

results_usj/int/01GENBSB_int.usj: bsb2usfm.py
	- $(PYTHON) bsb2usfm.py -I -o results_usj/int/^%BSB_int.usj -f demo_data/sample_footnotes.tsv -n demo_data/sample_book_names.xml

results_usj/strongs/01GENBSB_strongs.usj: bsb2usfm.py
	$(PYTHON) bsb2usfm.py -S -o results_usj/strongs/^%BSB_strongs.usj -f demo_data/sample_footnotes.tsv -n demo_data/sample_book_names.xml

results_usj/strongs_full/01GENBSB_full_strongs.usj: bsb2usfm.py
	$(PYTHON) bsb2usfm.py -S -P -B -o results_usj/strongs_full/^%BSB_full_strongs.usj -f demo_data/sample_footnotes.tsv -n demo_data/sample_book_names.xml