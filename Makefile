# Detect Python: try venv/bin/python, venv/bin/python3, then system python3
PYTHON=$(shell if [ -x venv/bin/python ]; then echo venv/bin/python; elif [ -x venv/bin/python3 ]; then echo venv/bin/python3; else echo python3; fi)

# Edition definitions
EDITIONS = bereanbible majoritybible

bereanbible_URL = https://bereanbible.com/bsb_tables.tsv
bereanbible_ID = BSB
bereanbible_SENTINEL = GEN

majoritybible_URL = https://majoritybible.com/msb_nt_tables.tsv
majoritybible_ID = MSB
majoritybible_SENTINEL = MAT

# PHONY targets that don't represent files
.PHONY: all clean clean-cache force refresh bereanbible majoritybible

all: bereanbible majoritybible

# Per-edition top-level targets
define EDITION_TARGETS
$(1): $(1)/results/$($(1)_SENTINEL).usfm \
      $(1)/results/int/$(call sentinel_int,$(1)).usfm \
      $(1)/results/strongs/$(call sentinel_strongs,$(1)).usfm \
      $(1)/results/strongs_full/$(call sentinel_full,$(1)).usfm \
      $(1)/results_usj/$($(1)_SENTINEL).usj \
      $(1)/results_usj/int/$(call sentinel_int,$(1)).usj \
      $(1)/results_usj/strongs/$(call sentinel_strongs,$(1)).usj \
      $(1)/results_usj/strongs_full/$(call sentinel_full,$(1)).usj \
      $(1)/results_usx/$($(1)_SENTINEL).usx \
      $(1)/results_usx/int/$(call sentinel_int,$(1)).usx \
      $(1)/results_usx/strongs/$(call sentinel_strongs,$(1)).usx \
      $(1)/results_usx/strongs_full/$(call sentinel_full,$(1)).usx
	$$(PYTHON) adapt_usx_for_DBL.py $(1)/results_usx -o $(1)/results_usx_for_DBL
	$$(PYTHON) adapt_usfm_for_paratext.py $(1)/results -o $(1)/results_for_paratext --identifier $($(1)_ID)
	$$(if $$(filter bereanbible,$(1)),cp demo_data/bsb_custom.vrs $(1)/sfm_for_paratext/custom.vrs,@:)
	$$(if $$(filter majoritybible,$(1)),$$(PYTHON) fix_msb.py --vrs-only,@:)
	$$(if $$(filter majoritybible,$(1)),cp majoritybible/msb.vrs $(1)/sfm_for_paratext/custom.vrs,@:)
	$$(if $$(filter majoritybible,$(1)),$$(PYTHON) mirror_bsb_ot_to_msb.py,@:)
	$$(PYTHON) create_zips.py --base-dir $(1) --identifier $($(1)_ID)
endef

# MSB collection includes BSB OT books; ensure BSB is built first.
majoritybible: bereanbible

# Helper functions for sentinel filenames
sentinel_int = $(call _bookcode,$(1))$($(1)_SENTINEL)$($(1)_ID)_int
sentinel_strongs = $(call _bookcode,$(1))$($(1)_SENTINEL)$($(1)_ID)_strongs
sentinel_full = $(call _bookcode,$(1))$($(1)_SENTINEL)$($(1)_ID)_full_strongs
_bookcode = $(if $(filter GEN,$($(1)_SENTINEL)),01,40)

# Generate edition targets
$(foreach ed,$(EDITIONS),$(eval $(call EDITION_TARGETS,$(ed))))

# Per-edition cache management
define EDITION_CACHE
$(1)/temp/source.tsv: | $(1)/temp
	@echo "Checking for updates from $($(1)_URL)..."
	@if [ -f "$$@" ]; then \
		curl -s -z "$$@" -o "$$@.tmp" "$($(1)_URL)"; \
		if [ -f "$$@.tmp" ]; then \
			echo "Remote file has been updated, using new version"; \
			mv "$$@.tmp" "$$@"; \
		else \
			echo "Using cached version (remote not modified)"; \
		fi \
	else \
		echo "Downloading $($(1)_URL) for the first time..."; \
		curl -s -o "$$@" "$($(1)_URL)"; \
	fi

$(1)/temp:
	mkdir -p $(1)/temp
endef

$(foreach ed,$(EDITIONS),$(eval $(call EDITION_CACHE,$(ed))))

# Per-edition build rules
define EDITION_RULES
# Basic USFM
$(1)/results/$($(1)_SENTINEL).usfm: bsb2usfm.py $(1)/temp/source.tsv
	mkdir -p $(1)/results
	- $$(PYTHON) bsb2usfm.py --identifier $($(1)_ID) -o $(1)/results/%.usfm -f demo_data/sample_footnotes.tsv $(1)/temp/source.tsv

# Interlinear USFM
$(1)/results/int/$(call sentinel_int,$(1)).usfm: bsb2usfm.py $(1)/temp/source.tsv
	mkdir -p $(1)/results/int
	- $$(PYTHON) bsb2usfm.py --identifier $($(1)_ID) -I -o $(1)/results/int/^%$($(1)_ID)_int.usfm -f demo_data/sample_footnotes.tsv $(1)/temp/source.tsv

# Strongs USFM
$(1)/results/strongs/$(call sentinel_strongs,$(1)).usfm: bsb2usfm.py $(1)/temp/source.tsv
	mkdir -p $(1)/results/strongs
	$$(PYTHON) bsb2usfm.py --identifier $($(1)_ID) -S -o $(1)/results/strongs/^%$($(1)_ID)_strongs.usfm -f demo_data/sample_footnotes.tsv $(1)/temp/source.tsv

# Strongs full USFM
$(1)/results/strongs_full/$(call sentinel_full,$(1)).usfm: bsb2usfm.py $(1)/temp/source.tsv
	mkdir -p $(1)/results/strongs_full
	$$(PYTHON) bsb2usfm.py --identifier $($(1)_ID) -S -P -B -o $(1)/results/strongs_full/^%$($(1)_ID)_full_strongs.usfm -f demo_data/sample_footnotes.tsv $(1)/temp/source.tsv

# Basic USJ
$(1)/results_usj/$($(1)_SENTINEL).usj: bsb2usfm.py $(1)/temp/source.tsv
	mkdir -p $(1)/results_usj
	- $$(PYTHON) bsb2usfm.py --identifier $($(1)_ID) -o $(1)/results_usj/%.usj -f demo_data/sample_footnotes.tsv $(1)/temp/source.tsv

# Interlinear USJ
$(1)/results_usj/int/$(call sentinel_int,$(1)).usj: bsb2usfm.py $(1)/temp/source.tsv
	mkdir -p $(1)/results_usj/int
	- $$(PYTHON) bsb2usfm.py --identifier $($(1)_ID) -I -o $(1)/results_usj/int/^%$($(1)_ID)_int.usj -f demo_data/sample_footnotes.tsv $(1)/temp/source.tsv

# Strongs USJ
$(1)/results_usj/strongs/$(call sentinel_strongs,$(1)).usj: bsb2usfm.py $(1)/temp/source.tsv
	mkdir -p $(1)/results_usj/strongs
	$$(PYTHON) bsb2usfm.py --identifier $($(1)_ID) -S -o $(1)/results_usj/strongs/^%$($(1)_ID)_strongs.usj -f demo_data/sample_footnotes.tsv $(1)/temp/source.tsv

# Strongs full USJ
$(1)/results_usj/strongs_full/$(call sentinel_full,$(1)).usj: bsb2usfm.py $(1)/temp/source.tsv
	mkdir -p $(1)/results_usj/strongs_full
	$$(PYTHON) bsb2usfm.py --identifier $($(1)_ID) -S -P -B -o $(1)/results_usj/strongs_full/^%$($(1)_ID)_full_strongs.usj -f demo_data/sample_footnotes.tsv $(1)/temp/source.tsv

# Basic USX
$(1)/results_usx/$($(1)_SENTINEL).usx: bsb2usfm.py $(1)/temp/source.tsv
	mkdir -p $(1)/results_usx
	- $$(PYTHON) bsb2usfm.py --identifier $($(1)_ID) -o $(1)/results_usx/%.usx -f demo_data/sample_footnotes.tsv $(1)/temp/source.tsv

# Interlinear USX
$(1)/results_usx/int/$(call sentinel_int,$(1)).usx: bsb2usfm.py $(1)/temp/source.tsv
	mkdir -p $(1)/results_usx/int
	- $$(PYTHON) bsb2usfm.py --identifier $($(1)_ID) -I -o $(1)/results_usx/int/^%$($(1)_ID)_int.usx -f demo_data/sample_footnotes.tsv $(1)/temp/source.tsv

# Strongs USX
$(1)/results_usx/strongs/$(call sentinel_strongs,$(1)).usx: bsb2usfm.py $(1)/temp/source.tsv
	mkdir -p $(1)/results_usx/strongs
	$$(PYTHON) bsb2usfm.py --identifier $($(1)_ID) -S -o $(1)/results_usx/strongs/^%$($(1)_ID)_strongs.usx -f demo_data/sample_footnotes.tsv $(1)/temp/source.tsv

# Strongs full USX
$(1)/results_usx/strongs_full/$(call sentinel_full,$(1)).usx: bsb2usfm.py $(1)/temp/source.tsv
	mkdir -p $(1)/results_usx/strongs_full
	$$(PYTHON) bsb2usfm.py --identifier $($(1)_ID) -S -P -B -o $(1)/results_usx/strongs_full/^%$($(1)_ID)_full_strongs.usx -f demo_data/sample_footnotes.tsv $(1)/temp/source.tsv
endef

$(foreach ed,$(EDITIONS),$(eval $(call EDITION_RULES,$(ed))))

# Force update by removing cache and rebuilding
force: clean-cache all

# Clean generated output files
clean:
	$(foreach ed,$(EDITIONS),rm -rf $(ed)/results $(ed)/results_usj $(ed)/results_usx $(ed)/results_usx_for_DBL $(ed)/results_for_paratext $(ed)/sfm_for_paratext $(ed)/workspace;)

# Clean the cached data files to force re-download
clean-cache:
	$(foreach ed,$(EDITIONS),rm -f $(ed)/temp/source.tsv;)

# Conditionally re-download cached sources only if upstream has been updated
# (uses HTTP If-Modified-Since via curl -z; no payload transfer on 304)
refresh:
	@$(foreach ed,$(EDITIONS), \
	    mkdir -p $(ed)/temp; \
	    rm -f $(ed)/temp/source.tsv.tmp; \
	    echo "$(ed): checking $($(ed)_URL) ..."; \
	    curl -s -z $(ed)/temp/source.tsv -o $(ed)/temp/source.tsv.tmp $($(ed)_URL); \
	    if [ -s $(ed)/temp/source.tsv.tmp ]; then \
	        echo "$(ed): updated"; \
	        mv $(ed)/temp/source.tsv.tmp $(ed)/temp/source.tsv; \
	    else \
	        echo "$(ed): up to date"; \
	        rm -f $(ed)/temp/source.tsv.tmp; \
	    fi;)
