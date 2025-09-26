#!/usr/bin/python3

import argparse, csv
import regex
import usfmtc
import xml.etree.ElementTree as et
from usfmtc.usfmparser import Grammar
from usfmtc.reference import Ref, RefRange, allbooks
from usfmtc.xmlutils import ParentElement

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
            para.text = m.group(i+1)
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
    "tab1":             Style("b", "pmo"),
    "tab1stline":       Style("pmo"),
    "tab1stlinered":    Style(["pmo", "wj"])
}

def debracket(s): return regex.sub(r"[\[\]{}]", "", s)

class Processor:
    def __init__(self, outname, books=None, fnqs=None, names=None):
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

    def writedoc(self):
        self.doc.canonicalise()
        self.doc.regularise()
        bk = self.doc.book
        if self.books is not None and bk not in self.books:
            return
        outfname = self.outname.replace("%", bk)
        print(f"Writing {outfname}")
        self.doc.saveAs(outfname)

    def addheadline(self, row):
        self.fields = row

    def makebook(self, bk):
        books = [booknames[allbooks.index(bk)], booknames[allbooks.index(bk)], bk]
        if self.names is not None:
            booke = self.names.find(f'.//book[@code="{bk}"]')
            if booke is not None:
                books = [booke.get(a, None) for a in ("long", "short", "abbr")]
        title1, title2 = booktitles.get(bk, (None, None))
        if title1 is None:
            if ' ' in books[0]:
                title1, title2 = books[0].rsplit(' ', 1)
            else:
                title1, title2 = books[0], books[0]
        template="""<?xml version="1.0" encoding="utf-8"?>
<usx version="3.1">
  <book style="id" code="{0}">Autogenerated BSB by bsb2usfm</book>
  <para style="h">{2}</para>
  <para style="toc1">{1}</para>
  <para style="toc2">{2}</para>
  <para style="toc3">{3}</para>
  <para style="mt2">{4}</para>
  <para style="mt1">{5}</para>
</usx>""".format(bk, *books, title1, title2)
        doc = usfmtc.USX.fromUsx(template)
        self.currnode = doc.getroot()[-1]  # Set to the last para element
        return doc

    def appenddoc(self, parent, tag, style, **attrib):
        attrib['style'] = style
        node = parent.makeelement(tag, attrib)
        parent.append(node)
        self.currnode = node
        return node

    def addheading(self, txt, isversetext=False):
        if self.currnode is None:
            return  # Skip heading if no current node is set
        if txt.startswith("<br />"):
            txt = txt[6:]
        txt = txt.strip()
        while len(txt):
            if txt.startswith("<p "):
                m = regex.match(r"<p class=\|(.*?)\|>(.*?)(?=$|<(?:p|span|div))", txt)
                if not m:
                    print(f"Heading p failed to parse: {txt}")
                    break
                c = ptypes.get(m.group(1), None)
                if c is None:
                    print(f"Missing ptype: {m.group(1)} in {txt}")
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
                rnode = currf.makeelement("ref", {"ref": str(r)})
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

    def appendtext(self, txt, isverse=True, dostrip=True):
        if self.currnode is None:
            print(f"Nothing to add text: {txt} to")
            return
        if dostrip:
            txt = txt.rstrip()
        if isverse and self.verse_pending:
            self.appendverse()
            txt = txt.lstrip()
        if len(self.currnode):
            self.currnode[-1].tail = (self.currnode[-1].tail or "") + txt
        else:
            self.currnode.text = (self.currnode.text or "") + txt

    def appendjunkytext(self, txt):
        while (m := regex.search(r"<p class=\|(.*?)\|>", txt)) != None:
            self.appendtext(txt[:m.start()])
            c = ptypes.get(m.group(1), None)
            if c is not None:
                self.currnode = c.addto(self.currnode)
            txt = txt[m.end():]
        if txt:
            self.appendtext(txt)

    def processline(self, row):
        f = {k: row[i] for i, k in enumerate(self.fields)}
        if f['VerseId']:
            print(f"Processing verse: {f['VerseId']}")
            m = regex.match(r"(\d?\s*\D+)\s*(\d+):(\d+)", f['VerseId'])
            if m is not None:
                print(f"Verse regex matched: {m.groups()}")
                lastref = self.cref
                self.cref = Ref(book=bookmap[m.group(1).strip()], chapter=int(m.group(2)), verse=int(m.group(3)))
                print(f"Created ref: {self.cref}")
                if self.doc is None or self.cref.book != self.doc.book:
                    print(f"Creating new document for book: {self.cref.book}")
                    if self.doc is not None:
                        self.writedoc()
                    self.doc = self.makebook(self.cref.book)
                    print(f"Document created, currnode: {self.currnode}")
                    lastref = Ref(book=self.cref.book)
                    self.skipping = self.books is not None and self.cref.book not in self.books
                if lastref is None or self.cref.chapter != lastref.chapter:
                    print(f"Adding chapter: {self.cref.chapter}")
                    self.appenddoc(self.doc.getroot(), "chapter", "c", number=str(self.cref.chapter))
                    print(f"Chapter added, currnode: {self.currnode}")
                self.fncount = 0
                self.verse_pending = True
            else:
                print(f"Failed to parse verse: {f['VerseId']}")
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
        if f[' BSB version ']:
            t = debracket(f[' BSB version '])
            if regex.match(r"^[\d,]+$", t):
                t = " " + t + " "
            if "<p class=" in t:
                self.appendjunkytext(t)
            elif t.strip() not in ('-', '. . .', 'vvv'):
                if self.pendinglstrip:
                    t = t.lstrip()
                    self.pendinglstrip = False
                self.appendtext(t)
        if f['pnc']:
            self.addend(f['pnc'])
        if row[20]:
            self.addend(debracket(row[20]))
        if f['footnotes']:
            self.addnote(f['footnotes'])
        if f['End text']:
            self.addend(f['End text'])


parser = argparse.ArgumentParser()
parser.add_argument("infile",help="Input bsb_tables.csv file")
parser.add_argument("-o","--outfile",help="Ouput usfm file template with % for the book code")
parser.add_argument("-f","--fnotes",help="Footnote styling tsv file")
parser.add_argument("-b","--book",action="append",help="Book codes to include")
parser.add_argument("-n","--names",help="BookNames.xml")
args = parser.parse_args()

fnqs = {}
if args.fnotes:
    with open(args.fnotes, encoding="utf-8") as inf:
        rdr = csv.reader(inf, delimiter = "\t")
        lastref = None
        for r in rdr:
            if r[0] == lastref:
                count += 1
                key = f"{r[0]}[{count}]"
            else:
                key = r[0]
            fnqs[key] = r[1:]

if args.names is not None:
    ndoc = et.parse(args.names)
else:
    ndoc = None

job = Processor(args.outfile, books=args.book, fnqs=(fnqs if len(fnqs) else None), names=ndoc)
with open(args.infile, encoding="utf-8") as inf:
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
