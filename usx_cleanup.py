#!/usr/bin/env python3
"""
General-purpose USX tree cleanups, applied to every generated book
regardless of output format (USX, USJ, USFM all serialize from the same
tree), independent of target (Paratext, DBL, plain USFM).

These are distinct from the USFM-3.0-vs-3.1 Paratext-validator shims in
adapt_usfm_for_paratext.py (custom \\ref -> \\xt, Strong's number padding,
\\wj splitting, "+" nesting, empty \\fqa before \\fv), which exist only to
work around Paratext's current basic checks on the serialized .usfm text
and are expected to become unnecessary once Paratext 9.6 ships full USFM
3.1 support. The fixes here have no such expiry — they correct things
that are wrong independent of version and output format.

Called from bsb2usfm.py's Processor.writedoc() after canonicalise()/
regularise() and before addesids(), so USX, USJ, and USFM output all
get them for free from a single tree-walking pass.
"""

import re

_BIBLICAL_BOOK_NAMES = {
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
    "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel",
    "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles",
    "Ezra", "Nehemiah", "Esther", "Job", "Psalm", "Psalms",
    "Proverbs", "Ecclesiastes", "Song of Solomon",
    "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel",
    "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah",
    "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi",
    "Matthew", "Mark", "Luke", "John", "Acts", "Romans",
    "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
    "1 Timothy", "2 Timothy", "Titus", "Philemon",
    "Hebrews", "James", "1 Peter", "2 Peter",
    "1 John", "2 John", "3 John", "Jude", "Revelation",
}


def _is_biblical_ref(display_text: str) -> bool:
    """Check if display text starts with a known biblical book name."""
    text = display_text.strip()
    for name in _BIBLICAL_BOOK_NAMES:
        if text.startswith(name):
            return True
    return False


def _is_valid_r_reference(ref: str) -> bool:
    """Check if a reference in an \\r line is a valid biblical reference.

    Must start with a known book name AND contain at least one number
    (chapter or chapter:verse). Book-only ranges like "Joshua-Malachi"
    (no numbers at all) are not valid.
    """
    if not _is_biblical_ref(ref):
        return False
    return bool(re.search(r"\d", ref))


def _is_empty(el) -> bool:
    """An element with no children and no non-whitespace text."""
    return not len(el) and not (el.text and el.text.strip())


def _unwrap(el) -> None:
    """Remove el from its parent, splicing its text+tail into the
    surrounding text flow (el must have no children)."""
    parent = el.getparent()
    if parent is None:
        return
    merged = (el.text or "") + (el.tail or "")
    idx = parent.index(el)
    if idx > 0:
        prev = parent[idx - 1]
        prev.tail = (prev.tail or "") + merged
    else:
        parent.text = (parent.text or "") + merged
    parent.remove(el)


def fix_mt_markers(root) -> int:
    """
    Fix \\mt2 + empty \\mt1 pattern by collapsing to a single \\mt1.

    Book title overrides can produce \\mt2 BookName followed by an empty
    \\mt1, which is flagged as an empty marker error. Simply removing the
    empty \\mt1 leaves only \\mt2, which is rejected because DBL requires
    a major title marker (\\mt or \\mt1) before chapter 1.

    Fix: fold \\mt2 BookName + empty \\mt1 into a single \\mt1 BookName.
    Any other standalone empty \\mt1 is removed outright.

    Returns count of fixes.
    """
    count = 0
    for para in list(root.iter("para")):
        if para.get("style") != "mt2" or not (para.text and para.text.strip()):
            continue
        nxt = para.getnext()
        if nxt is not None and nxt.tag == "para" and nxt.get("style") == "mt1" and _is_empty(nxt):
            para.set("style", "mt1")
            nxt.getparent().remove(nxt)
            count += 1

    for para in list(root.iter("para")):
        if para.get("style") == "mt1" and _is_empty(para):
            parent = para.getparent()
            if parent is not None:
                parent.remove(para)
                count += 1
    return count


def fix_nonbiblical_xt(root) -> int:
    """
    Convert \\xt markers for non-biblical books back to plain text.

    Reference checkers flag references to non-canonical books (Jasher,
    1 Enoch) even when they appear as plain text, but \\xt makes it
    worse. This unwraps xt char elements for those specific books back
    to plain text.

    Returns count of fixes.
    """
    count = 0
    for char in list(root.iter("char")):
        if char.get("style") != "xt" or len(char):
            continue
        text = char.text or ""
        if any(text.startswith(name) for name in ("Jasher", "1 Enoch")):
            _unwrap(char)
            count += 1
    return count


def fix_empty_ft(root) -> int:
    """
    Remove empty \\ft char elements (e.g. a footnote quote followed
    directly by a reference, with no footnote text of its own).

    Returns count of fixes.
    """
    count = 0
    for char in list(root.iter("char")):
        if char.get("style") == "ft" and _is_empty(char):
            _unwrap(char)
            count += 1
    return count


def remove_empty_para_markers(root) -> int:
    """
    Remove standalone empty \\q1 and \\p paragraphs.

    These appear as paragraphs with no text content, acting as visual
    separators, and are flagged as empty markers.

    Must run before addesids() — an empty paragraph can otherwise be
    used by addesids() as a vid-carrier for a verse span that crosses
    it, and removing it afterwards would silently drop that milestone
    metadata.

    Returns count of removals.
    """
    count = 0
    for para in list(root.iter("para")):
        if para.get("style") in ("q1", "p") and _is_empty(para):
            parent = para.getparent()
            if parent is not None:
                parent.remove(para)
                count += 1
    return count


def fix_mr_markers(root) -> int:
    """
    Convert \\mr to \\d.

    \\mr (major section reference range) at end of book causes
    "Marker cannot occur here" errors. \\d (descriptive title)
    is the appropriate marker for psalm/song attributions like
    "For the choirmaster. With stringed instruments."

    Returns count of fixes.
    """
    count = 0
    for para in root.iter("para"):
        if para.get("style") == "mr":
            para.set("style", "d")
            count += 1
    return count


def remove_invalid_r_markers(root) -> int:
    """
    Remove \\r paragraphs that contain references that cannot be
    validated: non-biblical references or book-only references without
    chapter:verse.

    Biblical \\r paragraphs with proper chapter:verse references are
    kept.

    Returns count of removals.
    """
    count = 0
    for para in list(root.iter("para")):
        if para.get("style") != "r":
            continue
        refs = [child for child in para if child.tag == "ref"]
        if refs:
            texts = [(child.text or "").strip() for child in refs]
        else:
            texts = [(para.text or "").strip(" ()")]
        if not all(texts):
            continue
        if any(not _is_valid_r_reference(t) for t in texts):
            parent = para.getparent()
            if parent is not None:
                parent.remove(para)
                count += 1
    return count


def apply(root) -> None:
    """Run all general-purpose tree cleanups in sequence, in place."""
    fix_mt_markers(root)
    fix_nonbiblical_xt(root)
    fix_empty_ft(root)
    remove_empty_para_markers(root)
    fix_mr_markers(root)
    remove_invalid_r_markers(root)
