#!/usr/bin/env python3

"""
Demo Data Creator for BSB to USFM Converter
This script creates sample data files for testing the converter
"""

import os
import csv
from pathlib import Path

def create_demo_directories():
    """Create demo data directory structure"""
    demo_dir = Path("demo_data")
    demo_dir.mkdir(exist_ok=True)
    return demo_dir

def create_footnote_styling(demo_dir):
    """Create a sample footnote styling TSV file"""

    footnote_data = [
        ["GEN 1:5", "fqa", "ft"],
        ["GEN 1:5[1]", "fq", "ft"],
        ["EXO 3:14", "fqa", "ft"],
        ["JHN 3:16", "fq", "ft", "fqa"],
        ["JHN 3:16[1]", "fqa", "ft"]
    ]

    file_path = demo_dir / "sample_footnotes.tsv"
    with open(file_path, 'w', newline='', encoding='utf-8') as tsvfile:
        writer = csv.writer(tsvfile, delimiter='\t')
        writer.writerows(footnote_data)

    print(f"✓ Created footnote styling: {file_path}")
    return file_path

def create_book_names(demo_dir):
    """Create a sample BookNames.xml file"""

    xml_content = '''<?xml version="1.0" encoding="utf-8"?>
<books>
    <!-- Old Testament Books -->
    <book code="GEN" long="Genesis" short="Genesis" abbr="Gen"/>
    <book code="EXO" long="Exodus" short="Exodus" abbr="Exo"/>
    <book code="LEV" long="Leviticus" short="Leviticus" abbr="Lev"/>
    <book code="NUM" long="Numbers" short="Numbers" abbr="Num"/>
    <book code="DEU" long="Deuteronomy" short="Deuteronomy" abbr="Deu"/>

    <!-- New Testament Books -->
    <book code="MAT" long="The Gospel According to Matthew" short="Matthew" abbr="Mat"/>
    <book code="MRK" long="The Gospel According to Mark" short="Mark" abbr="Mrk"/>
    <book code="LUK" long="The Gospel According to Luke" short="Luke" abbr="Luk"/>
    <book code="JHN" long="The Gospel According to John" short="John" abbr="Jhn"/>
    <book code="ACT" long="The Acts of the Apostles" short="Acts" abbr="Act"/>
    <book code="ROM" long="The Letter to the Romans" short="Romans" abbr="Rom"/>
    <book code="1CO" long="The First Letter to the Corinthians" short="1 Corinthians" abbr="1Co"/>
    <book code="2CO" long="The Second Letter to the Corinthians" short="2 Corinthians" abbr="2Co"/>
    <book code="GAL" long="The Letter to the Galatians" short="Galatians" abbr="Gal"/>
    <book code="EPH" long="The Letter to the Ephesians" short="Ephesians" abbr="Eph"/>
    <book code="PHP" long="The Letter to the Philippians" short="Philippians" abbr="Php"/>
    <book code="COL" long="The Letter to the Colossians" short="Colossians" abbr="Col"/>
    <book code="1TH" long="The First Letter to the Thessalonians" short="1 Thessalonians" abbr="1Th"/>
    <book code="2TH" long="The Second Letter to the Thessalonians" short="2 Thessalonians" abbr="2Th"/>
    <book code="1TI" long="The First Letter to Timothy" short="1 Timothy" abbr="1Ti"/>
    <book code="2TI" long="The Second Letter to Timothy" short="2 Timothy" abbr="2Ti"/>
    <book code="TIT" long="The Letter to Titus" short="Titus" abbr="Tit"/>
    <book code="PHM" long="The Letter to Philemon" short="Philemon" abbr="Phm"/>
    <book code="HEB" long="The Letter to the Hebrews" short="Hebrews" abbr="Heb"/>
    <book code="JAS" long="The Letter of James" short="James" abbr="Jas"/>
    <book code="1PE" long="The First Letter of Peter" short="1 Peter" abbr="1Pe"/>
    <book code="2PE" long="The Second Letter of Peter" short="2 Peter" abbr="2Pe"/>
    <book code="1JN" long="The First Letter of John" short="1 John" abbr="1Jn"/>
    <book code="2JN" long="The Second Letter of John" short="2 John" abbr="2Jn"/>
    <book code="3JN" long="The Third Letter of John" short="3 John" abbr="3Jn"/>
    <book code="JUD" long="The Letter of Jude" short="Jude" abbr="Jud"/>
    <book code="REV" long="The Revelation to John" short="Revelation" abbr="Rev"/>
</books>'''

    file_path = demo_dir / "sample_book_names.xml"
    with open(file_path, 'w', encoding='utf-8') as xmlfile:
        xmlfile.write(xml_content)

    print(f"✓ Created book names: {file_path}")
    return file_path

def create_readme(demo_dir, bsb_file, footnote_file, names_file):
    """Create a README file explaining the demo data"""

    readme_content = f"""# Demo Data for BSB to USFM Converter

This directory contains sample data files for testing the BSB to USFM converter.

## Files Created

### 1. {bsb_file.name}
Sample BSB tables data containing verses from:
- Genesis 1:1-5 (Creation narrative)
- Exodus 3:14 (God's name revealed)
- Matthew 1:1-2 (Jesus' genealogy with heading)
- John 3:16 (Gospel verse with footnote)
- Revelation 22:20-21 (Bible's closing verses)

**Features demonstrated:**
- Basic verse text
- Red letter text (Jesus' words)
- Headings and formatting
- Footnotes with various styling
- Mixed Old and New Testament content
- Tab-delimited format (TSV)

### 2. {footnote_file.name}
Footnote styling rules for the sample verses:
- Different footnote types (fq, fqa, ft)
- Multiple footnotes per verse
- Hebrew and Greek term explanations

### 3. {names_file.name}
Custom book names with:
- Long names (formal titles)
- Short names (common usage)
- Abbreviations (3-letter codes)
- Both Old and New Testament examples

## Usage Examples

### Command Line
```bash
# Convert all books
python3 bsb2usfm.py /data/bsb_tables.csv -o demo_output_%.usfm

# With footnotes and custom names
python3 bsb2usfm.py /data/bsb_tables.csv \\
  -o demo_output_%.usfm \\
  -f demo_data/{footnote_file.name} \\
  -n demo_data/{names_file.name}

# Convert specific books only
python3 bsb2usfm.py /data/bsb_tables.csv \\
  -o demo_output_%.usfm \\
  -b GEN -b MAT -b JHN -b REV
```

### Web Interface
1. Start the web server: `./run_web.py`
2. Visit: http://localhost:5000
4. Optionally upload `{footnote_file.name}` and `{names_file.name}`
5. Select books or leave empty for all
6. Click "Convert to USFM"
7. Download your results

## Expected Output

The conversion should generate USFM files like:

### demo_output_GEN.usfm
```usfm
\\id GEN Autogenerated BSB by bsb2usfm
\\h Gen
\\toc1 Genesis
\\toc2 Genesis
\\toc3 GEN
\\mt1 Genesis
\\c 1
\\v 1 In the beginning God created the heavens and the earth.
\\v 2 Now the earth was formless and void...
```

### demo_output_MAT.usfm
```usfm
\\id MAT Autogenerated BSB by bsb2usfm
\\h Mat
\\toc1 The Gospel According to Matthew
\\toc2 Matthew
\\toc3 MAT
\\mt1 The Gospel According to Matthew
\\s1 The Genealogy of Jesus Christ
\\c 1
\\v 1 This is the record of the genealogy...
```

## Notes

- This is sample data for demonstration purposes
- Real BSB data will have many more verses and complex formatting
- The footnote styling may need adjustment for your specific needs
- Book names can be customized for different language traditions

## Troubleshooting

If conversion fails:
1. Check that all files are UTF-8 encoded
2. Verify the TSV structure matches expected format (tab-delimited)
3. Ensure footnote references match verse IDs exactly
4. Check that XML is well-formed

For more help, see the main README.md file.
"""

    readme_path = demo_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as readme:
        readme.write(readme_content)

    print(f"✓ Created README: {readme_path}")
    return readme_path

def main():
    """Create all demo data files"""

    print("=" * 50)
    print("  Creating Demo Data for BSB to USFM Converter")
    print("=" * 50)
    print()

    # Create directory structure
    demo_dir = create_demo_directories()
    print(f"📁 Demo directory: {demo_dir.absolute()}")
    print()

    # Create sample files
    footnote_file = create_footnote_styling(demo_dir)
    names_file = create_book_names(demo_dir)
    readme_file = create_readme(demo_dir, footnote_file, names_file)

    print()
    print("=" * 50)
    print("  Demo Data Created Successfully!")
    print("=" * 50)
    print()
    print("Quick Test Commands:")
    print()
    print("  # Command line conversion:")
    print(f"  python3 bsb2usfm.py /data/bsb_tables.csv -o demo_%.usfm")
    print()
    print("  # With all optional files:")
    print(f"  python3 bsb2usfm.py /data/bsb_tables.csv \\")
    print(f"    -o demo_%.usfm \\")
    print(f"    -f {footnote_file} \\")
    print(f"    -n {names_file}")
    print()
    print("  # Web interface:")
    print("  ./run_web.py")
    print("  # Then upload files at http://localhost:5000")
    print()
    print("Files created:")
    for file_path in [footnote_file, names_file, readme_file]:
        print(f"  - {file_path}")
    print()

if __name__ == "__main__":
    main()
