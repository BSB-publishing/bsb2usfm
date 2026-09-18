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
    Convert cross-references to non-biblical books back to plain text.

    Reference checkers flag references to non-canonical books (Jasher,
    1 Enoch) even when they appear as plain text, but a cross-reference
    marker makes it worse. bsb2usfm.py's addnote() represents these as
    <ref loc="..."> elements (canonref() still returns a Ref even when
    the book name doesn't resolve, so a <ref> gets built regardless) —
    usfmtc's USFM/SFM serializer renders a bare <ref> as \\xt, which is
    where the "\\xt Jasher ...\\xt*" / "\\xt 1 Enoch ...\\xt*" markers
    Paratext complains about actually come from. This unwraps <ref>
    elements (and, for good measure, any <char style="xt">) for those
    specific books back to plain text before that serialization happens.

    Returns count of fixes.
    """
    count = 0
    for el in list(root.iter("ref")) + list(root.iter("char")):
        if el.tag == "char" and (el.get("style") != "xt" or len(el)):
            continue
        if el.tag == "ref" and len(el):
            continue
        text = el.text or ""
        if any(text.startswith(name) for name in ("Jasher", "1 Enoch")):
            _unwrap(el)
            count += 1
    return count


def fix_empty_ft(root) -> int:
    """
    Remove empty \\ft char elements (e.g. a footnote quote followed
    directly by a reference, with no footnote text of its own).

    A \\ft that wraps nothing but a nested reference (e.g.
    "\\ft \\ref Genesis 50:25|GEN 50:25\\ref*\\f*", from addnote()
    building a bare <ref> child with no explanatory text of its own)
    counts as empty too, even though it has a child — Paratext flags
    it as an empty marker regardless. Promote the child(ren) to take
    the \\ft's place instead of just unwrapping plain text.

    Returns count of fixes.
    """
    count = 0
    for char in list(root.iter("char")):
        if char.get("style") != "ft" or (char.text and char.text.strip()):
            continue
        if not len(char):
            _unwrap(char)
            count += 1
            continue
        children = list(char)
        for child in children:
            char.addprevious(child)
        children[-1].tail = (children[-1].tail or "") + (char.tail or "")
        parent = char.getparent()
        if parent is not None:
            parent.remove(char)
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


def merge_adjacent_add(root) -> int:
    """
    Merge \\add spans separated only by whitespace into a single span.

    bsb2usfm.py creates one \\add char element per bracket-delimited
    segment in the source data (e.g. "The name of the first {river} {is}
    the Pishon" -> two adjacent \\add spans with nothing but a space
    between them). Paratext's checks flag this as the same character
    style being closed and immediately reopened. Since nothing but
    whitespace separates them, they're really one continuous added
    phrase — merge them, keeping the whitespace as part of the combined
    \\add text so the rendered spacing is unchanged.

    Returns count of merges.
    """
    count = 0
    parents = []
    seen = set()
    for char in root.iter("char"):
        if char.get("style") != "add":
            continue
        parent = char.getparent()
        if parent is not None and id(parent) not in seen:
            seen.add(id(parent))
            parents.append(parent)

    def is_add(el):
        return el is not None and el.tag == "char" and el.get("style") == "add"

    for parent in parents:
        i = 0
        children = list(parent)
        while i < len(children):
            child = children[i]
            if is_add(child) and not (child.tail or "").strip() and i + 1 < len(children) and is_add(children[i + 1]):
                nxt = children[i + 1]
                child.text = (child.text or "") + (child.tail or "") + (nxt.text or "")
                for grandchild in list(nxt):
                    child.append(grandchild)
                child.tail = nxt.tail
                parent.remove(nxt)
                count += 1
                children = list(parent)
            else:
                i += 1
    return count


def split_multiword_w(root) -> int:
    """
    Split a \\w/\\rb span at an internal clause-boundary comma,
    semicolon, "!", "?", or dash into two spans sharing the same
    alignment attribute, with the punctuation relocated between them.

    The source TSV aligns one Hebrew/Greek word per row, but a
    translator-supplied connective with no word of its own in the
    original (e.g. "Meanwhile,", "Quick!") gets bundled into the same
    cell as the next aligned word rather than given its own row (e.g.
    "Meanwhile, Abraham" or "Quick! Prepare" aligned to a single
    source word). bsb2usfm.py wraps that whole cell in one \\w span,
    which Paratext's word check rejects because of the embedded
    punctuation. Splitting preserves the alignment (both spans keep
    the same strong/gloss attribute) and the rendered text — only the
    punctuation moves from inside the span to between the two spans.

    Only splits on punctuation immediately followed by whitespace, so
    a numeral's thousands-separator comma ("46,500", no following
    space) and a spaced ellipsis (". . .") are never touched.

    Returns count of splits.
    """
    count = 0
    pattern = re.compile(r"^(.*?)([,;!?—–]\s+)(.*)$", re.DOTALL)
    for char in list(root.iter("char")):
        if char.get("style") not in ("w", "rb") or len(char):
            continue
        cur = char
        while True:
            m = pattern.match(cur.text or "")
            if not m or not m.group(1).strip() or not m.group(3).strip():
                break
            first, sep, rest = m.group(1).rstrip(), m.group(2), m.group(3)
            cur.text = first
            sib = cur.makeelement(cur.tag, dict(cur.attrib))
            sib.text = rest
            sib.tail = cur.tail
            cur.tail = sep
            # rest may start with a quote/bracket carried over from the
            # split point (e.g. "saying, "Indeed, ..." splits into
            # "saying" + ", " + ""Indeed, ..."), which would leave the
            # new span starting with a non-word-forming character —
            # relocate it into the separator, after the space already
            # placed there.
            if (lm := re.match(r'^[\s"“”\[(]+', sib.text)) is not None and lm.end() < len(sib.text):
                cur.tail += sib.text[:lm.end()]
                sib.text = sib.text[lm.end():]
            cur.addnext(sib)
            count += 1
            cur = sib
    return count


def fix_typographic_spacing(root) -> int:
    """
    Remove stray whitespace immediately before a comma, semicolon, or
    question mark, and immediately inside an opening or closing
    parenthesis (e.g. "Nevertheless , the" -> "Nevertheless, the",
    "( that is" -> "(that is", "is )" -> "is)").

    These are typos in the upstream source data (a single word-aligned
    cell containing the stray space, e.g. one cell holding "Likewise ,
    every"), not something introduced by this pipeline, but nothing
    downstream corrects them either. Deliberately narrow: only touches
    whitespace directly adjacent to ,;?() — never periods, so the
    spaced-ellipsis house style (". . .") is untouched even when it
    immediately precedes a closing paren (only the trailing space
    before the paren is removed, e.g. ". . . )" -> ". . .)").

    Returns count of fixes.
    """
    count = 0
    pattern = re.compile(r"\s+([,;?)])|(\()\s+")

    def fix(s):
        nonlocal count
        if s is None:
            return s
        new, n = pattern.subn(lambda m: (m.group(1) or "") + (m.group(2) or ""), s)
        count += n
        return new

    for el in root.iter():
        el.text = fix(el.text)
        el.tail = fix(el.tail)
    return count


def apply(root) -> None:
    """Run all general-purpose tree cleanups in sequence, in place."""
    fix_mt_markers(root)
    fix_nonbiblical_xt(root)
    fix_empty_ft(root)
    remove_empty_para_markers(root)
    fix_mr_markers(root)
    remove_invalid_r_markers(root)
    merge_adjacent_add(root)
    split_multiword_w(root)
    fix_typographic_spacing(root)
