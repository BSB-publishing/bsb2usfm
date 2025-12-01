PYTHON ?= venv/bin/python3
REMOTE_URL = https://bereanbible.com/bsb_tables.tsv
CACHED_DATA = temp/bsb_tables.tsv

# PHONY targets that don't represent files
.PHONY: all clean clean-cache force check-remote-updates

all: results/GEN.usfm results/int/01GENBSB_int.usfm results/strongs/01GENBSB_strongs.usfm results/strongs_full/01GENBSB_full_strongs.usfm results_usj/GEN.usj results_usj/int/01GENBSB_int.usj results_usj/strongs/01GENBSB_strongs.usj results_usj/strongs_full/01GENBSB_full_strongs.usj
	$(PYTHON) create_zips.py

COMMON = -f demo_data/sample_footnotes.tsv -n demo_data/sample_book_names.xml 

# Always check for updates from remote (PHONY target)
check-remote-updates: | temp
	@echo "Checking for updates from $(REMOTE_URL)..."
	@if [ -f "$(CACHED_DATA)" ]; then \
		curl -s -z "$(CACHED_DATA)" -o "$(CACHED_DATA).tmp" "$(REMOTE_URL)"; \
		if [ -f "$(CACHED_DATA).tmp" ]; then \
			echo "Remote file has been updated, using new version"; \
			mv "$(CACHED_DATA).tmp" "$(CACHED_DATA)"; \
		else \
			echo "Using cached version (remote not modified)"; \
		fi \
	else \
		echo "Downloading $(REMOTE_URL) for the first time..."; \
		curl -s -o "$(CACHED_DATA)" "$(REMOTE_URL)"; \
	fi

# Download and cache the remote data file with timestamp checking
# This uses curl with -z flag to only download if remote is newer
$(CACHED_DATA): check-remote-updates

# Ensure temp directory exists
temp:
	mkdir -p temp

# Force update by removing cache and rebuilding
force: clean-cache all

# All output files depend on both the script and the cached data
results/GEN.usfm: bsb2usfm.py $(CACHED_DATA)
	- $(PYTHON) bsb2usfm.py -o results/%.usfm ${COMMON} $(CACHED_DATA)

results/int/01GENBSB_int.usfm: bsb2usfm.py $(CACHED_DATA)
	- $(PYTHON) bsb2usfm.py -I -o results/int/^%BSB_int.usfm ${COMMON} $(CACHED_DATA)

results/strongs/01GENBSB_strongs.usfm: bsb2usfm.py $(CACHED_DATA)
	$(PYTHON) bsb2usfm.py -S -o results/strongs/^%BSB_strongs.usfm ${COMMON} $(CACHED_DATA)

results/strongs_full/01GENBSB_full_strongs.usfm: bsb2usfm.py $(CACHED_DATA)
	$(PYTHON) bsb2usfm.py -S -P -B -o results/strongs_full/^%BSB_full_strongs.usfm ${COMMON} $(CACHED_DATA)

results_usj/GEN.usj: bsb2usfm.py $(CACHED_DATA)
	- $(PYTHON) bsb2usfm.py -o results_usj/%.usj ${COMMON} $(CACHED_DATA)

results_usj/int/01GENBSB_int.usj: bsb2usfm.py $(CACHED_DATA)
	- $(PYTHON) bsb2usfm.py -I -o results_usj/int/^%BSB_int.usj ${COMMON} $(CACHED_DATA)

results_usj/strongs/01GENBSB_strongs.usj: bsb2usfm.py $(CACHED_DATA)
	$(PYTHON) bsb2usfm.py -S -o results_usj/strongs/^%BSB_strongs.usj ${COMMON} $(CACHED_DATA)

results_usj/strongs_full/01GENBSB_full_strongs.usj: bsb2usfm.py $(CACHED_DATA)
	$(PYTHON) bsb2usfm.py -S -P -B -o results_usj/strongs_full/^%BSB_full_strongs.usj ${COMMON} $(CACHED_DATA)

# Clean generated output files
clean:
	rm -f results/*.usfm results/int/*.usfm results/strongs/*.usfm results/strongs_full/*.usfm
	rm -f results_usj/*.usj results_usj/int/*.usj results_usj/strongs/*.usj results_usj/strongs_full/*.usj

# Clean the cached data file to force re-download
clean-cache:
	rm -f $(CACHED_DATA)
