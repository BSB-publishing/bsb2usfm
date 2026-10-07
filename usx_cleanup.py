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

# Non-word-forming punctuation that Paratext's \w/\rb word check rejects
# inside a span, shared by bsb2usfm.py's leading/trailing boundary-trim and
# this module's embedded-punctuation splitting so the set only needs
# extending in one place. Deliberately excludes ' and ’ (legitimate
# word-medial/-final characters in English possessives/contractions, e.g.
# "brother's", "Levites’" — a Paratext project-setting fix, not a markup
# bug — see PARATEXT_ADAPTATIONS.md) and digits.
NONWORD_PUNCTUATION = '.,;!?()[]"“”‘—–…'

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
    Remove truly empty \\ft char elements: no text and no children.

    A \\ft whose only content is a nested reference (e.g.
    "\\ft \\ref Genesis 50:25|GEN 50:25\\ref*\\f*", from addnote()
    building a bare <ref> child with no explanatory text of its own) is
    valid USFM and is kept here. Paratext's basic checks flag it as an
    empty marker, so adapt_usfm_for_paratext.py removes that \\ft from
    the Paratext deliverable only (fix_empty_ft_before_xt).

    Returns count of fixes.
    """
    count = 0
    for char in list(root.iter("char")):
        if char.get("style") != "ft" or len(char) or (char.text and char.text.strip()):
            continue
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
            if (lm := re.match(f'^[\\s{re.escape(NONWORD_PUNCTUATION)}]+', sib.text)) is not None and lm.end() < len(sib.text):
                cur.tail += sib.text[:lm.end()]
                sib.text = sib.text[lm.end():]
            cur.addnext(sib)
            count += 1
            cur = sib
    return count


_EMBEDDED_BOUNDARY_CHARS = set(NONWORD_PUNCTUATION)


def split_embedded_punctuation_w(root) -> int:
    """
    Split a \\w/\\rb span at punctuation embedded strictly inside a
    multi-word aligned phrase (e.g. "Baal-hermon (that is", "the
    Levites) were given", "or ‘Mother", "Stop!” they cry") — never at
    the very start or end of the span's text, which appendtext()
    already keeps clean.

    Uses a tokenizer rather than a single regex so a numeral's
    thousands-separator comma ("46,500") and hyphenated compounds
    ("Baal-hermon") are never touched, while adjacent punctuation of
    different kinds (a comma immediately followed by a closing quote,
    an "!" immediately followed by a closing quote) is treated as one
    run and relocated together. Whitespace immediately touching a
    punctuation run moves with it into the tail between the two
    resulting spans; whitespace between two ordinary words (e.g. "the
    boy") is left alone, since \\w spans routinely wrap whole phrases.

    Returns count of splits.
    """
    count = 0

    def tokenize(text):
        tokens = []
        i, n = 0, len(text)
        while i < n:
            is_boundary = text[i] in _EMBEDDED_BOUNDARY_CHARS
            j = i + 1
            while j < n and (text[j] in _EMBEDDED_BOUNDARY_CHARS) == is_boundary:
                j += 1
            tokens.append(["punct" if is_boundary else "word", text[i:j]])
            i = j
        return tokens

    for char in list(root.iter("char")):
        if char.get("style") not in ("w", "rb") or len(char):
            continue
        tokens = tokenize(char.text or "")
        if len(tokens) < 3 or tokens[0][0] == "punct" or tokens[-1][0] == "punct":
            continue  # nothing embedded, or a leading/trailing case appendtext() handles

        # Keep a numeral's thousands-separator comma inside its word token
        # (e.g. "46" "," "500" -> "46,500") rather than splitting on it.
        merged = []
        i = 0
        while i < len(tokens):
            kind, val = tokens[i]
            if (kind == "punct" and val == "," and merged and merged[-1][0] == "word"
                    and merged[-1][1][-1:].isdigit() and i + 1 < len(tokens)
                    and tokens[i + 1][0] == "word" and tokens[i + 1][1][:1].isdigit()):
                merged[-1][1] += val + tokens[i + 1][1]
                i += 2
                continue
            merged.append([kind, val])
            i += 1
        tokens = merged
        if len(tokens) < 3 or tokens[0][0] == "punct" or tokens[-1][0] == "punct":
            continue

        # Whitespace touching a punctuation run travels with it, so the
        # resulting word spans never themselves start/end in whitespace.
        for i, (kind, val) in enumerate(tokens):
            if kind != "punct":
                continue
            if i > 0 and tokens[i - 1][0] == "word":
                stripped = tokens[i - 1][1].rstrip()
                trailing_ws = tokens[i - 1][1][len(stripped):]
                if trailing_ws:
                    tokens[i - 1][1] = stripped
                    tokens[i][1] = trailing_ws + tokens[i][1]
            if i < len(tokens) - 1 and tokens[i + 1][0] == "word":
                stripped = tokens[i + 1][1].lstrip()
                leading_ws = tokens[i + 1][1][:len(tokens[i + 1][1]) - len(stripped)]
                if leading_ws:
                    tokens[i + 1][1] = stripped
                    tokens[i][1] = tokens[i][1] + leading_ws

        cur = char
        cur.text = tokens[0][1]
        pending_tail = ""
        for kind, val in tokens[1:]:
            if kind == "punct":
                pending_tail += val
                continue
            sib = cur.makeelement(cur.tag, dict(cur.attrib))
            sib.text = val
            sib.tail = cur.tail
            cur.tail = pending_tail
            cur.addnext(sib)
            cur = sib
            pending_tail = ""
            count += 1
        if pending_tail:
            cur.tail = pending_tail + (cur.tail or "")

    return count


def remove_punctuation_only_w(root) -> int:
    """
    Drop the \\w/\\rb wrapper around a span whose entire content is
    punctuation (e.g. a lone "(" or ". . .)"). The source TSV aligns
    one word per row, but a stray punctuation mark with no word of its
    own sometimes lands in the same cell as an adjacent word's Strong's
    number, so bsb2usfm.py ends up wrapping it in its own \\w span.
    Paratext's word check rejects a \\w span with no word-forming
    character at all. Since there's no real word here, the wrapper is
    simply removed and its text relocated to the nearest sibling's
    tail — the rendered text is unchanged, only the markup around it.

    Returns count of removals.
    """
    boundary = _EMBEDDED_BOUNDARY_CHARS | {" ", "\n", "\t"}
    count = 0
    for char in list(root.iter("char")):
        if char.get("style") not in ("w", "rb") or len(char):
            continue
        text = char.text or ""
        if not text or any(c not in boundary for c in text):
            continue
        parent = char.parent
        if parent is None:
            continue
        siblings = list(parent)
        idx = siblings.index(char)
        tail = text + (char.tail or "")
        if idx > 0:
            prev = siblings[idx - 1]
            prev.tail = (prev.tail or "") + tail
        else:
            parent.text = (parent.text or "") + tail
        parent.remove(char)
        count += 1
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
    split_embedded_punctuation_w(root)
    remove_punctuation_only_w(root)
    fix_typographic_spacing(root)
