#!/usr/bin/python3

import argparse, csv
import regex
import usfmtc
import xml.etree.ElementTree as et
from usfmtc.usfmparser import Grammar
import urllib.request
import sys
import io
from usfmtc.reference import Ref, RefRange, allbooks, bookcodes


category_types = {
    "char": ["char", "footnotechar", "crossreferencechar", "listchar", "introchar"],
    "para": ["header", "introduction", "list", "otherpara", "sectionpara", "title", "versepara"]
}
categories = {v: k for k, l in category_types.items() for v in l}

def ensurespace(n):
    if not len(n):
        if n.text and not n.text[-1] in " \n":
            n.text += " "
    elif n[-1].tail and not n[-1].tail[-1] in " \n":
        n[-1].tail += " "
    else:
        ensurespace(n[-1])

def removeentities(s):
    s = regex.sub(r"&#([\d]+);", lambda m:chr(int(m.group(1), 10)), s)
    s = regex.sub(r"&#x([\dA-Fa-f]+);", lambda m:chr(int(m.group(1), 16)), s)
    return s

class Style:
    def __init__(self, styles, after=None):
        if isinstance(styles, str):
            styles = [styles]
        self.styles = styles
        self.after = after

    def addto(self, parent, text=None, ispar=False, verse=None):
        res = None
        for s in self.styles:
            if s == "b" and parent is not None \
                    and Grammar.marker_categories.get(parent.get("style", None), None) == "sectionpara":
                continue
            t = categories.get(Grammar.marker_categories.get(s, ""), None)
            if t is None:
                continue
            if t == "para" or ispar:
                while parent.parent is not None:
                    parent = parent.parent
            if ispar and t != "para":
                pres = parent.makeelement("para", {"style": "p"})
                parent.append(pres)
                parent = pres
            if verse is not None and t != "para":
                pres = parent.makeelement("verse", {"style": "v", "number": str(verse.verse)})
                parent.append(pres)
                verse = None
            if t != "para":
                ensurespace(parent)
            res = parent.makeelement(t, {"style": s})
            parent.append(res)
            parent = res
            ispar = False       # only interested for the first style
        if res is None:
            print(f"Bad styles: {self.styles}")
        elif text is not None:
            res.text = text
        if self.after is not None:
            t = categories.get(Grammar.marker_categories.get(self.after, ""), None)
            if t is not None:
                tnode = parent.makeelement(t, {"style": self.after})
                parent.append(tnode)
        return res


class AcrosticStyle:
    def __init__(self, styles):
        self.styles = styles

    def addto(self, parent, text=None, ispar=False, verse=None):
        if text is None:
            return None
        m = regex.match(r"(.*?)<br> (.*)", text)
        if not m:
            return
        while parent.parent is not None:
            parent = parent.parent
        para = None
        for i in range(2):
            para = parent.makeelement("para", {"style": self.styles[i]})
            para.text = removeentities(m.group(i+1))
            parent.append(para)
        return para


booknames = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges", "Ruth",
        "1 Samuel", "2 Samuel", "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra",
        "Nehemiah", "Esther", "Job", "Psalm", "Proverbs", "Ecclesiastes", "Song of Solomon",
        "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
        "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi",
        "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1 Corinthians", "2 Corinthians",
        "Galatians", "Ephesians", "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
        "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James", "1 Peter", "2 Peter",
        "1 John", "2 John", "3 John", "Jude", "Revelation"]

booktitles = {
    "ECC":  ("The Preacher, or", "Ecclesiastes"),
    "SNG":  ("The Song of Solomon, or", "Song of Songs"),
    "ACT":  ("The Acts of the Apostles", "Acts"),
    "REV":  ("The Revelation to John", "Revelation"),
}

bookmap = {booknames[i]: allbooks[i] for i in range(len(booknames))}

def canonref(s):
    m = regex.search(r"((?:\d\s*)?\S+)\s*(\d+):(\d+)([-\u2013](\d+)(:(\d+))?)?", s)
    if not m:
        return (None, 0, 0)
    res = Ref(book=bookmap.get(m.group(1).strip()), chapter=int(m.group(2)), verse=int(m.group(3)))
    if m.group(4):
        if m.group(6):
            kw = {"verse": int(m.group(7)), "chapter": int(m.group(5))}
        else:
            kw = {"verse": int(m.group(5))}
        res = RefRange(res, res.copy(**kw))
    return (res, m.start(), m.end())


ptypes = {
    "acrostic":         AcrosticStyle(["qa", "qa"]),
    "cross":            Style("r"),
    "fnv":              Style("fv"),         # regex(r"(.*)"), lambda m: [char("fv", m.group(1))]),
    "hdg":              Style("s1"),         # regex(r"(.*)"), lambda m: [para("s1", m.group(1))]),
    "ihdg":             Style("s2"),         # regex(r"(.*)"), lambda m: [para("s2", m.group(1))]),
    "indent1":          Style("q1"),
    "indent1stline":    Style(["b", "q1"]),
    "indent1stlinered": Style(["q1", "wj"]),
    "indent2":          Style("q2"),
    "indentred1":       Style(["q1", "wj"]),
    "indentred2":       Style(["q2", "wj"]),
    "inscrip":          Style("pc"),
    "list1":            Style("li1"),
    "list1stline":      Style(["b", "li1"]),
    "list2":            Style("li2"),
    "pshdg":            Style("mr"),
    "red":              Style("wj"),
    "reftext":          ("v"),      # \v 1 at the start of the psalm after the heading. special handling
    "reg":              Style("p"),
    "selah":            Style("qr"),
    "subhdg":           Style("s2"),
    "suphdg":           Style("ms"),
    "tab1":             Style(["b", "pmo"]),
    "tab1stline":       Style("pmo"),
    "tab1stlinered":    Style(["pmo", "wj"])
}

def debracket(s): return regex.sub(r"[\[\]{}]", "", s)

class Processor:
    def __init__(self, outname, books=None, fnqs=None, names=None, interlinear=False, strongs=False, placeholders=False, brackets=False, identifier="BSB"):
        self.doc = None
        self.currnode = None
        self.cref = None
        self.outname = outname
        self.books = books
        self.fnqs = fnqs
        self.fncount = 0
        self.pendinglstrip = False
        self.names = names
        self.skipping = False
        self.verse_pending = False
        self.interlinear = interlinear
        self.strongs = strongs
        self.placeholders = placeholders
        self.brackets = brackets
        self.identifier = identifier

    def writedoc(self):
        bk = self.doc.book
        if self.books is not None and bk not in self.books:
            return
        self.doc.canonicalise()
        self.doc.regularise()
        bkcode = bookcodes.get(bk, '99')
        outfname = self.outname.replace("%", bk).replace('^', bkcode)
        print(f"Writing {outfname}")
        self.doc.saveAs(outfname)

    def addheadline(self, row):
        self.fields = row
        # Detect version column name dynamically (e.g. " BSB version " or " MSB version ")
        self.version_col = None
        self.interlinear_col = None
        for f in row:
            if f.strip().endswith('version'):
                self.version_col = f
            if f.startswith('WLC / Nestle') or f == 'MT Greek':
                if self.interlinear_col is None:
                    self.interlinear_col = f

    def makebook(self, bk):
        books = [booknames[allbooks.index(bk)], booknames[allbooks.index(bk)], bk]
        if self.names is not None:
            booke = self.names.find(f'.//book[@code="{bk}"]')
            if booke is not None:
                books = [booke.get(a, None) for a in ("long", "short", "abbr")]
        title1, title2 = booktitles.get(bk, (None, None))
        if title1 is None:
            title1, title2 = books[0].rsplit(' ', 1) if ' ' in books[0] else (books[0], "")
        template="""<?xml version="1.0" encoding="utf-8"?>
<usx version="3.1">
  <book style="id" code="{0}">Autogenerated {6} by bsb2usfm</book>
  <para style="h">{2}</para>
  <para style="toc1">{1}</para>
  <para style="toc2">{2}</para>
  <para style="toc3">{3}</para>
  <para style="mt2">{4}</para>
  <para style="mt1">{5}</para>
</usx>""".format(bk, *books, title1, title2, self.identifier)
        doc = usfmtc.USX.fromUsx(template)
        self.currnode = doc.getroot()
        return doc

    def appenddoc(self, parent, tag, style, **attrib):
        attrib['style'] = style
        node = parent.makeelement(tag, attrib)
        parent.append(node)
        self.currnode = node
        return node

    def addheading(self, txt, isversetext=False):
        if txt.startswith("<br />"):
            txt = txt[6:]
        txt = txt.strip()
        while len(txt):
            if txt.startswith("<p "):
                m = regex.match(r"<p class=\|(.*?)\|>(.*?)(?=$|<(?:p|span|div))", txt)
                if not m:
                    print(f"Heading p failed to parse: {txt}")
                    break
                t = m.group(1)
                if t == "pshdg" and self.verse_pending:
                    c = Style("d")
                else:
                    c = ptypes.get(t, None)
                if c is None:
                    print(f"Missing ptype: {t} in {txt}")
                    break
                self.currnode = c.addto(self.currnode, m.group(2).strip(), ispar=True,
                                verse=self.cref if self.verse_pending and isversetext else None)
                if isversetext and self.currnode.tag == "char":
                    self.verse_pending = False
                txt = txt[m.end():]
            elif txt.startswith("<span "):
                m = regex.match(r"<span class=\|(.*?)\|>(.*?)(</span>|$)", txt)
                if not m:
                    print(f"Bad span: {txt}")
                    break
                c = ptypes.get(m.group(1), None)
                if c is None:
                    print(f"Missing ptype for span: {m.group(1)} in {txt}")
                    break
                self.currnode = c.addto(self.currnode)
                bits = regex.split(r"<a.*?>(.*?)</a>", m.group(2))
                for i, b in enumerate(bits):
                    if i == 0:
                        self.currnode.text = b
                    elif i % 2 == 0:
                        c.tail = b
                    else:
                        bref, x, xx = canonref(b)
                        c = self.currnode.makeelement("ref", {} if bref is None else {"loc": str(bref)})
                        c.text = b
                        self.currnode.append(c)
                txt = txt[m.end():]
            elif txt.startswith("<div "):
                m = regex.match(r"<div class=\|(.*?)\|>(.*?)(</div>|$)", txt)
                if not m:
                    print(f"Bad div: {txt}")
                    break
                c = ptypes.get(m.group(1), None)
                if c is None:
                    print(f"Missing ptype for div: {m.group(1)} in {txt}")
                    break
                self.currnode = c.addto(self.currnode, m.group(2))
                txt = txt[m.end():]
            else:
                print(f"Unknown heading text to process: {txt}")
                break
        self.pendinglstrip = False

    def addnote(self, txt):
        bits = regex.split(r"</?i>", txt)
        fnode = self.currnode.makeelement("note", {"style": "f", "caller": "+"})
        self.currnode.append(fnode)
        if self.cref:
            currf = fnode.makeelement("char", {"style": "fr"})
            currf.text = f"{self.cref.chapter}:{self.cref.verse} "
            fnode.append(currf)
        fqs = []
        if self.fnqs is not None:
            fqs = self.fnqs.get(str(self.cref) + ("" if self.fncount == 0 else f"[{self.fncount}]"), [])
        qcount = 0
        for i, b in enumerate(bits):
            if not len(b):
                continue
            prevf = currf
            currf = fnode.makeelement("char", {"style": "ft" if i % 2 == 0 else (fqs[qcount] if qcount < len(fqs) else "fqa")})
            qcount += 1
            b = removeentities(b)
            r, j, e = canonref(b)
            if r is None:
                count = 0
                vnode = currf
                while (m := regex.search(r"<span class=\|fnv\|>(.*?)</span>", b)) is not None:
                    if count == 0:
                        currf.text = b[:m.start()]
                    else:
                        vnode.tail = b[:m.start()]
                    n = currf.makeelement("char", {"style": "fv"})
                    currf.append(n)
                    n.text = m.group(1)
                    vnode = n
                    b = b[m.end():]
                    count += 1
                if count > 0:
                    vnode.tail = b
                elif b.startswith(" "):
                    prevf.text = (prevf.text or "") + " "
                    currf.text = b[1:]
                else:
                    currf.text = b
            else:
                currf.text = b[:j]
                rnode = currf.makeelement("ref", {"loc": str(r)})
                currf.append(rnode)
                rnode.text = b[j:e]
                rnode.tail = b[e:]
            fnode.append(currf)
        self.fncount += 1

    def addend(self, txt):
        bits = regex.split(r"</(?:span|div)>", txt)
        for i, b in enumerate(bits):
            if i != 0:
                self.currnode = self.currnode.parent
            self.appendtext(b)

    def appendverse(self):
        vnode = self.currnode.makeelement("verse", {"style": "v", "number": str(self.cref.verse)})
        self.currnode.append(vnode)
        self.verse_pending = False

    def appendtext(self, txt, alt=None, mode=None, isverse=True, dostrip=True):
        if self.currnode is None:
            print(f"Nothing to add text: {txt} to")
            return
        if dostrip:
            txt = txt.rstrip()
        if isverse and self.verse_pending:
            self.appendverse()
            txt = txt.lstrip()
        txt = removeentities(txt)
        node = None
        if mode == "interlinear":
            node = self.currnode.makeelement('char', {"style": 'rb', "gloss": alt})
        elif mode == "strongs":
            node = self.currnode.makeelement('char', {"style": "w", 'strong': alt})
        if node is not None:
            if (m := regex.match(r"^\s+", txt)) is not None:
                node.text = txt[m.end():]
                if len(self.currnode):
                    self.currnode[-1].tail = (self.currnode[-1].tail or "") + txt[:m.end()]
                else:
                    self.currnode.text = (self.currnode.text or "") + txt[:m.end()]
            else:
                node.text = txt
            self.currnode.append(node)
        elif len(self.currnode):
            self.currnode[-1].tail = (self.currnode[-1].tail or "") + txt
        else:
            self.currnode.text = (self.currnode.text or "") + txt

    def appendjunkytext(self, txt, alt=None, mode=None):
        while (m := regex.search(r"<p class=\|(.*?)\|>", txt)) != None:
            self.appendtext(txt[:m.start()], alt=alt, mode=mode)
            c = ptypes.get(m.group(1), None)
            if c is not None:
                self.currnode = c.addto(self.currnode)
            txt = txt[m.end():]
            rb = None
        if txt:
            self.appendtext(txt, alt=alt, mode=mode)

    def processline(self, row):
        f = {k: row[i] for i, k in enumerate(self.fields)}
        if f['VerseId']:
            m = regex.match(r"(\d?\s*\D+)\s*(\d+):(\d+)", f['VerseId'])
            if m is not None:
                lastref = self.cref
                self.cref = Ref(book=bookmap[m.group(1).strip()], chapter=int(m.group(2)), verse=int(m.group(3)))
                if self.doc is None or self.cref.book != self.doc.book:
                    if self.doc is not None:
                        self.writedoc()
                    self.doc = self.makebook(self.cref.book)
                    lastref = Ref(book=self.cref.book)
                    self.skipping = self.books is not None and self.cref.book not in self.books
                if lastref is None or self.cref.chapter != lastref.chapter:
                    self.appenddoc(self.doc.getroot(), "chapter", "c", number=str(self.cref.chapter))
                self.fncount = 0
                self.verse_pending = True
        if self.skipping:
            return
        if f['Hdg']:
            self.addheading(f['Hdg'])
        if f['Crossref']:
            self.addheading(f['Crossref'])
        if f['Par']:
            self.addheading(f['Par'], isversetext=True)
        if row[17]:
            if not row[17].startswith("<span class=|reftext|"):
                self.appendtext(" "+debracket(row[17]))
            self.pendinglstrip = True
        bsb_content = f[self.version_col] if f[self.version_col] else ('. . .' if self.strongs and self.placeholders and (f['Str Heb'] or f['Str Grk']) else None)
        isblank = False
        t = None
        if bsb_content:
            # handling self.brackets
            t = debracket(bsb_content) if not self.brackets else bsb_content
            if regex.match(r"^[\d,]+$", t):
                t = " " + t + " "
            # handling self.placeholders
            isblank = not self.placeholders and t.strip() in ('-', '. . .', 'vvv')
        if t:
            # handling self.brackets
            iword = None
            mode = None
            if self.interlinear:
                iword = f.get(self.interlinear_col, None) if self.interlinear_col else None
                mode = "interlinear"
            elif self.strongs:
                for a in ('Heb', 'Grk'):
                    if f['Str '+a]:
                        iword = a[0]+f['Str '+a]
                        mode = "strongs"
                        break
            if "<p class=" in t:
                self.appendjunkytext(t, alt=iword, mode=mode)
            elif not isblank or self.interlinear:
                if self.pendinglstrip:
                    t = t.lstrip()
                    self.pendinglstrip = False
                if t.strip() == "( -":
                    t = " ("
                    self.pendinglstrip = True
                if isblank:
                    t = ""
                self.appendtext(t, alt=iword, mode=mode)
        if f['pnc']:
            self.addend(f['pnc'])
        if row[20]:
            self.addend(debracket(row[20]))
        if f['footnotes']:
            self.addnote(f['footnotes'])
        if f['End text']:
            self.addend(f['End text'])

parser = argparse.ArgumentParser()
parser.add_argument("infile",nargs="?",default=None,help="Input bsb_tables.csv file or URL (default: https://bereanbible.com/bsb_tables.tsv)")
parser.add_argument("-o","--outfile",help="Ouput usfm file template with %% for the book code, ^ for number")
parser.add_argument("-f","--fnotes",help="Footnote styling tsv file")
parser.add_argument("-b","--book",action="append",help="Book codes to include")
parser.add_argument("-n","--names",help="BookNames.xml")
# Add optional flags (default is None)
parser.add_argument("-I","--interlinear",action="store_true",help="Output \\rb entries for reverse interlinear")
parser.add_argument('-S','--strongs',action='store_true',help='Include Strong\'s numbers')
parser.add_argument('-P','--placeholders',action='store_true',help='Include placeholders')
parser.add_argument('-B','--brackets',action='store_true',help='Include brackets')
parser.add_argument('--identifier',default='BSB',help='Edition identifier (default: BSB)')

args = parser.parse_args()

if args.interlinear and args.strongs:
    print("You cannot have both interlinear and strongs numbers in the same file")
    sys.exit(1)

# Set default URL if no input file specified
if args.infile is None:
    args.infile = "https://bereanbible.com/bsb_tables.tsv"

# Function to open input from URL or local file
def open_input_source(source):
    """Open input from either a URL or local file path"""
    if source.startswith(("http://", "https://")):
        print(f"Downloading from {source}...", file=sys.stderr)
        response = urllib.request.urlopen(source)
        content = response.read().decode("utf-8")
        return io.StringIO(content)
    else:
        # Try UTF-8 first, then fall back to UTF-16
        for encoding in ['utf-8', 'utf-16']:
            try:
                f = open(source, encoding=encoding)
                # Try to read first line to validate encoding
                f.readline()
                f.seek(0)
                print(f"Using encoding: {encoding}", file=sys.stderr)
                return f
            except (UnicodeDecodeError, UnicodeError):
                continue
        # If both fail, use default
        return open(source, encoding='utf-8')

fnqs = {}
if args.fnotes:
    with open(args.fnotes, encoding="utf-8") as inf:
        rdr = csv.reader(inf, delimiter = "\t")
        lastref = None
        count = 0
        for r in rdr:
            if r[0] == lastref:
                count += 1
                key = f"{r[0]}[{count}]"
            else:
                count = 0
                lastref = r[0]
                key = r[0]
            fnqs[key] = r[1:]

if args.names is not None:
    ndoc = et.parse(args.names)
else:
    ndoc = None

job = Processor(args.outfile, books=args.book, fnqs=(fnqs if len(fnqs) else None),
                              names=ndoc, interlinear=args.interlinear, strongs=args.strongs,
                              placeholders=args.placeholders, brackets=args.brackets,
                              identifier=args.identifier)
with open_input_source(args.infile) as inf:
    rdr = csv.reader(inf, delimiter="\t")
    hdr = None
    for r in rdr:
        if hdr is None:
            hdr = r
            if r[0].startswith("//"):
                hdr = None
            else:
                job.addheadline(r)
            continue
        job.processline(r)
    job.writedoc()
