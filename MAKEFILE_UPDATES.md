# Makefile Updates - Remote File Timestamp Checking

## Problem
The original Makefile only checked if `bsb2usfm.py` was newer than the output files. This meant that if the remote data source (`https://bereanbible.com/bsb_tables.tsv`) was updated, running `make all` would not regenerate the output files unless you manually deleted them or modified the Python script.

## Solution
The updated Makefile now:

1. **Downloads and caches the remote data file** to `temp/bsb_tables.tsv`
2. **Checks the remote file's Last-Modified timestamp** using `curl -z` flag
3. **Only downloads if the remote file is newer** than the cached version
4. **Makes all output files depend on the cached data file** so they rebuild when the remote data changes

## How It Works

### Cached Data Rule
```makefile
$(CACHED_DATA): | temp
    @echo "Checking for updates from $(REMOTE_URL)..."
    @if [ -f "$(CACHED_DATA)" ]; then \
        curl -s -z "$(CACHED_DATA)" -o "$(CACHED_DATA).tmp" "$(REMOTE_URL)"; \
        ...
```

This rule:
- **Runs on every build** to check for remote updates (using .PHONY target)
- Uses `curl -z` (time conditional) to only download if remote is newer
- Downloads to a temporary file first
- Only replaces the cached file if a new version was downloaded
- The cached file's timestamp reflects when it was last updated from the remote

### Dependencies
All output files now depend on both `bsb2usfm.py` AND `$(CACHED_DATA)`:

```makefile
results/GEN.usfm: bsb2usfm.py $(CACHED_DATA)
    - $(PYTHON) bsb2usfm.py -o results/%.usfm ... $(CACHED_DATA)
```

This means output files will be regenerated if EITHER:
- The Python script is modified, OR
- The remote data file is updated

## Usage

### Normal Build
```bash
make all
```
This will:
1. **Always check** if the remote file has been updated (on every build)
2. Download it if newer (or skip if unchanged)
3. Regenerate output files if either:
   - The cached data was updated from remote, OR
   - The Python script was modified
4. Create zip files

### Force Complete Rebuild
```bash
make force
```
This removes the cached data file and rebuilds everything from scratch.

### Clean Output Files
```bash
make clean
```
Removes all generated USFM and USJ files.

### Clean Cache Only
```bash
make clean-cache
```
Removes only the cached data file, forcing a fresh download on next build.

## Benefits

1. **Automatic updates**: Running `make all` always checks and detects remote data changes
2. **Efficient**: Only downloads the full file if the remote is actually newer
3. **Faster builds**: Uses local cache when remote hasn't changed (only HTTP HEAD check)
4. **Single download per build**: Each build command checks once and caches the result
5. **Standard make behavior**: Respects timestamp-based dependency checking for regenerating outputs
6. **No manual intervention**: You never need to manually delete files to get updates

## Requirements

- `curl` must be installed (standard on most Unix-like systems)
- Internet connection required to check for remote updates

## Technical Details

### How the Remote Check Works

The Makefile uses a `.PHONY` target `check-remote-updates` that runs on every build. This target uses `curl -z` which performs a conditional GET request:

1. **Sends the local file's timestamp** to the remote server
2. **Server compares** with its Last-Modified header
3. **If remote is newer**: curl downloads to a temporary file, then we replace the cache
4. **If remote is same/older**: curl exits without creating output file (cache unchanged)

This approach means:
- **Every `make all` checks for updates** (unavoidable for detecting remote changes)
- **Full download only happens** when remote is actually newer
- **Network overhead is minimal** when file hasn't changed (just HTTP headers)
- **Timestamp-based rebuilds** work correctly because cache file timestamp reflects actual updates

### Why This Approach?

Make's dependency system is based on file modification times. Since the remote file doesn't exist in the local filesystem, we need to:
1. Download/check it to know if it changed
2. Store it locally so make can compare timestamps
3. Always check on builds to detect remote updates

Alternative approaches (like checking only every N hours) would miss updates and defeat the purpose of the improvement.