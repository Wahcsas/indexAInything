from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


# =========================
# KONFIGURATION
# =========================
INPUT_DOCX = r"C:\Users\Daniel\Downloads\josefa_bib\Dahlke_USA_Bibliographie.docx"
OUTPUT_DOCX = r"C:\Users\Daniel\Downloads\josefa_bib\Dahlke_USA_Bibliographie_umgestellt.docx"

# Optional: nur einen Bereich im Dokument bearbeiten (Start/End-Marker als Absatztext)
USE_MARKERS = False
START_MARKER_TEXT = "Literaturverzeichnis"
END_MARKER_TEXT = ""  # leer = bis Dokumentende


# =========================
# HELFER
# =========================
def _is_blank_paragraph_text(text: str) -> bool:
    return not text or not text.strip()


def _is_ders_dies_paragraph(text: str) -> bool:
    # Nur wenn exakt am Zeilenanfang (ggf. mit Whitespace davor)
    return re.match(r"^\s*(Ders|Dies)\.:\s*", text) is not None


def _normalize_sort_key(s: str) -> str:
    s = s.strip().casefold()
    s = (s.replace("ä", "ae")
           .replace("ö", "oe")
           .replace("ü", "ue")
           .replace("ß", "ss"))
    s = re.sub(r"[^a-z0-9 ]+", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _clean_given(given: str) -> str:
    # Whitespace normalisieren, damit z.B. "Lien-Hang T.  (Hrsg.)" -> "Lien-Hang T. (Hrsg.)"
    given = given.replace("\u00A0", " ")  # NBSP -> Space
    given = re.sub(r"\s+", " ", given).strip()
    return given


# =========================
# FORMAT-SNAPSHOT/APPLY
# =========================
def _snapshot_run_format(run) -> dict:
    f = run.font
    return {
        "bold": run.bold,
        "italic": run.italic,
        "underline": run.underline,
        "style": run.style,
        "font_name": f.name,
        "font_size": f.size,
        "small_caps": f.small_caps,
        "all_caps": f.all_caps,
        "superscript": f.superscript,
        "subscript": f.subscript,
        "highlight": f.highlight_color,
    }


def _apply_run_format(new_run, fmt: Optional[dict]) -> None:
    if not fmt:
        return
    new_run.bold = fmt.get("bold")
    new_run.italic = fmt.get("italic")
    new_run.underline = fmt.get("underline")
    if fmt.get("style") is not None:
        new_run.style = fmt.get("style")
    f = new_run.font
    f.name = fmt.get("font_name")
    f.size = fmt.get("font_size")
    f.small_caps = fmt.get("small_caps")
    f.all_caps = fmt.get("all_caps")
    f.superscript = fmt.get("superscript")
    f.subscript = fmt.get("subscript")
    try:
        f.highlight_color = fmt.get("highlight")
    except Exception:
        pass


# =========================
# AUTOR-PARSING
# =========================
@dataclass
class AuthorParse:
    surname: str
    given: str
    colon_idx: int
    is_mononym: bool
    surname_fmt: Optional[dict] = None
    given_fmt: Optional[dict] = None


def _find_colon_index(paragraph_text: str) -> int:
    return paragraph_text.find(":")


def _extract_author_parts_by_smallcaps(paragraph) -> Optional[AuthorParse]:
    """
    Erkennt Autorenteil vor dem ersten ':'.

    Normalfall:
      Vorname(n) NACHNAME (ggf. + (Hrsg.)) : ...
      -> surname (small_caps/all_caps), given (rest)

    Mononym-Fall:
      NACHNAME: ...
      -> is_mononym=True, bleibt unverändert (nur Sortkey)
    """
    full_text = paragraph.text

    # Safety: "Ders./Dies." sollen NIE umgestellt werden
    if _is_ders_dies_paragraph(full_text):
        return None

    colon_idx = _find_colon_index(full_text)
    if colon_idx <= 0:
        return None

    before_text = full_text[:colon_idx]
    if not before_text.strip():
        return None

    pos = 0
    surname_parts: List[str] = []
    given_parts: List[str] = []

    saw_caps_run = False
    surname_fmt = None
    given_fmt = None

    for run in paragraph.runs:
        t = run.text or ""
        if not t:
            continue

        run_start = pos
        run_end = pos + len(t)
        pos = run_end

        if run_start >= colon_idx:
            continue

        clip_end = min(run_end, colon_idx)
        clip_text = t[: max(0, clip_end - run_start)]
        if not clip_text:
            continue

        is_caps = bool(run.font.small_caps) or bool(run.font.all_caps)

        if is_caps and re.search(r"[A-Za-zÄÖÜäöüß]", clip_text):
            saw_caps_run = True
            surname_parts.append(clip_text)
            if surname_fmt is None:
                surname_fmt = _snapshot_run_format(run)
        else:
            given_parts.append(clip_text)
            if given_fmt is None and re.search(r"[A-Za-zÄÖÜäöüß]", clip_text):
                given_fmt = _snapshot_run_format(run)

    surname = "".join(surname_parts).strip()
    given = "".join(given_parts).strip()

    # Mononym: vor ':' besteht praktisch nur aus Kapitälchen-Name, sonst nix.
    # Wir erlauben dabei Whitespace + Punkt/Komma/Bindestrich/Nummern etc.
    given_stripped = re.sub(r"[\s\.,;:()\-\u00A0]+", "", given)
    if saw_caps_run and surname and not given_stripped:
        return AuthorParse(
            surname=surname,
            given="",
            colon_idx=colon_idx,
            is_mononym=True,
            surname_fmt=surname_fmt,
            given_fmt=given_fmt,
        )

    # Normalfall: wir brauchen beides
    if not surname or not given.strip():
        # Fallback, falls SmallCaps nicht sauber vorhanden ist:
        m = re.search(r"(.+?)\s+([A-ZÄÖÜ][A-ZÄÖÜß\- ]+)$", before_text.strip())
        if not m:
            return None
        given = m.group(1).strip()
        surname = m.group(2).strip()

    if not surname or not given:
        return None

    return AuthorParse(
        surname=surname,
        given=given,
        colon_idx=colon_idx,
        is_mononym=False,
        surname_fmt=surname_fmt,
        given_fmt=given_fmt,
    )


# =========================
# XML-HILFEN (Hyperlinks erhalten)
# =========================
def _iter_text_nodes(elem):
    for t in elem.iter(qn("w:t")):
        yield t


def _elem_text_len(elem) -> int:
    return sum(len(t.text or "") for t in _iter_text_nodes(elem))


def _trim_elem_left(elem, n: int) -> None:
    if n <= 0:
        return
    for t in _iter_text_nodes(elem):
        s = t.text or ""
        if not s:
            continue
        if n >= len(s):
            n -= len(s)
            t.text = ""
        else:
            t.text = s[n:]
            return


def _lstrip_elem_spaces(elem) -> None:
    for t in _iter_text_nodes(elem):
        s = t.text or ""
        if not s:
            continue
        new = s.lstrip(" ")
        t.text = new
        if new:
            return


def _remove_prefix_up_to_colon_keep_suffix(paragraph, colon_idx: int) -> None:
    """
    Entfernt im Absatz-XML alles bis inkl. ':' anhand Textindex.
    Lässt den Suffix-XML-Baum unangetastet (Hyperlinks bleiben).
    """
    p = paragraph._p
    boundary = colon_idx + 1  # inklusive ':'

    children = [c for c in list(p) if not c.tag.endswith("}pPr")]

    pos = 0
    first_remaining_elem = None

    for child in children:
        child_len = _elem_text_len(child)

        if child_len == 0:
            if pos < boundary:
                p.remove(child)
            else:
                if first_remaining_elem is None:
                    first_remaining_elem = child
            continue

        if pos + child_len <= boundary:
            p.remove(child)
            pos += child_len
            continue

        if pos < boundary < pos + child_len:
            _trim_elem_left(child, boundary - pos)
            if first_remaining_elem is None:
                first_remaining_elem = child
            pos += child_len
            continue

        if first_remaining_elem is None:
            first_remaining_elem = child
        pos += child_len

    if first_remaining_elem is not None:
        _lstrip_elem_spaces(first_remaining_elem)


def _insert_prefix_runs(paragraph, surname: str, given: str, surname_fmt: Optional[dict], given_fmt: Optional[dict]) -> None:
    """
    Fügt Prefix-Runs vorne ein (nach pPr), ohne den Suffix zu zerstören.
    """
    p = paragraph._p

    insert_idx = 0
    for i, c in enumerate(list(p)):
        if c.tag.endswith("}pPr"):
            insert_idx = i + 1
            break

    created_run_elems = []

    # SURNAME in Kapitälchen
    r1 = paragraph.add_run(surname)
    _apply_run_format(r1, surname_fmt)
    r1.font.small_caps = True
    created_run_elems.append(r1._r)

    # ", "
    r2 = paragraph.add_run(", ")
    _apply_run_format(r2, surname_fmt or given_fmt)
    created_run_elems.append(r2._r)

    # Given (inkl. (Hrsg.) etc.)
    r3 = paragraph.add_run(given)
    _apply_run_format(r3, given_fmt or surname_fmt)
    created_run_elems.append(r3._r)

    # ": "
    r4 = paragraph.add_run(": ")
    _apply_run_format(r4, given_fmt or surname_fmt)
    created_run_elems.append(r4._r)

    # Runs wurden am Ende angehängt -> nach vorne verschieben
    for r in created_run_elems:
        p.remove(r)
    for r in created_run_elems[::-1]:
        p.insert(insert_idx, r)


def swap_author_in_paragraph_preserve_links(paragraph) -> Optional[str]:
    """
    Stellt Autorenteil um und erhält Suffix inkl. Hyperlinks.
    Rückgabe: Nachname (für Sortierung) oder None (wenn nicht erkannt).
    """
    parsed = _extract_author_parts_by_smallcaps(paragraph)
    if parsed is None:
        return None

    # Mononym: nicht anfassen
    if parsed.is_mononym:
        return parsed.surname

    given_clean = _clean_given(parsed.given)

    _remove_prefix_up_to_colon_keep_suffix(paragraph, parsed.colon_idx)

    _insert_prefix_runs(
        paragraph,
        surname=parsed.surname.strip(),
        given=given_clean,
        surname_fmt=parsed.surname_fmt,
        given_fmt=parsed.given_fmt,
    )

    return parsed.surname


# =========================
# EINTRÄGE GRUPPIEREN / SORTIEREN
# =========================
@dataclass
class Entry:
    paragraphs: List  # docx Paragraph objects
    surname_for_sort: str


def _collect_entries(paragraphs) -> List[Entry]:
    """
    Gruppierung:

    - Wenn es im Dokument Leerzeilen gibt: Ein Eintrag = Block aus nicht-leeren Absätzen bis zur Leerzeile.
      (Ders./Dies. stehen ja typischerweise ohne Leerzeile direkt darunter und bleiben damit im Block.)

    - Wenn es KEINE Leerzeilen gibt: normal jeder Absatz eigener Eintrag,
      ABER Absätze, die mit 'Ders.:' oder 'Dies.:' beginnen, werden an den vorherigen Eintrag angehängt.
    """
    has_any_blank = any(_is_blank_paragraph_text(p.text) for p in paragraphs)

    if has_any_blank:
        groups: List[List] = []
        current: List = []

        for p in paragraphs:
            if _is_blank_paragraph_text(p.text):
                if current:
                    groups.append(current)
                    current = []
            else:
                current.append(p)

        if current:
            groups.append(current)

        return [Entry(g, "") for g in groups]

    # Keine Leerzeilen: jeder Absatz eigenes Entry, außer Ders./Dies -> an vorheriges Entry dran
    groups: List[List] = []
    for p in paragraphs:
        if _is_blank_paragraph_text(p.text):
            continue

        if _is_ders_dies_paragraph(p.text) and groups:
            groups[-1].append(p)
        else:
            groups.append([p])

    return [Entry(g, "") for g in groups]


def _subset_by_markers(doc: Document) -> List:
    paras = doc.paragraphs
    if not USE_MARKERS:
        return paras

    start_idx = 0
    end_idx = len(paras)

    for i, p in enumerate(paras):
        if p.text.strip() == START_MARKER_TEXT.strip():
            start_idx = i + 1
            break

    if END_MARKER_TEXT.strip():
        for i in range(start_idx, len(paras)):
            if paras[i].text.strip() == END_MARKER_TEXT.strip():
                end_idx = i
                break

    return paras[start_idx:end_idx]


def _reorder_document_paragraphs(doc: Document, sorted_entries: List[Entry], keep_blank_lines: bool = True) -> None:
    """
    Schreibt den Dokument-Body neu (nur Paragraph-Elemente).
    Warnung: funktioniert für "Absatz-Dokumente" ohne Tabellen im Body.
    """
    body = doc._body._element
    children = list(body)

    sectPr = None
    for c in children:
        if c.tag.endswith("}sectPr"):
            sectPr = c
            break

    has_table = any(c.tag.endswith("}tbl") for c in children)
    if has_table:
        raise RuntimeError("Dokument enthält Tabellen. Dieses Skript sortiert nur reine Absatz-Dokumente (keine Tabellen im Body).")

    # Alles außer sectPr entfernen
    for c in list(body):
        if sectPr is not None and c is sectPr:
            continue
        body.remove(c)

    # Sortierte Absätze wieder einfügen
    for idx, entry in enumerate(sorted_entries):
        for p in entry.paragraphs:
            body.append(p._p)
        if keep_blank_lines and idx < len(sorted_entries) - 1:
            body.append(OxmlElement("w:p"))

    # sectPr ans Ende
    if sectPr is not None and (len(body) == 0 or body[-1] is not sectPr):
        if sectPr.getparent() is None:
            body.append(sectPr)


# =========================
# MAIN
# =========================
def main() -> None:
    doc = Document(INPUT_DOCX)
    target_paras = _subset_by_markers(doc)
    entries = _collect_entries(target_paras)

    # 1) Umstellen + Sortkey
    for entry in entries:
        p0 = entry.paragraphs[0]

        surname = swap_author_in_paragraph_preserve_links(p0)
        if surname is None:
            entry.surname_for_sort = _normalize_sort_key(p0.text)
        else:
            entry.surname_for_sort = _normalize_sort_key(surname)

    # 2) Sortieren (Ders./Dies bleiben im jeweiligen Entry-Block)
    entries.sort(key=lambda e: e.surname_for_sort)

    # 3) Neu anordnen
    _reorder_document_paragraphs(doc, entries, keep_blank_lines=True)

    # 4) Speichern
    doc.save(OUTPUT_DOCX)
    print(f"Fertig. Gespeichert unter: {OUTPUT_DOCX}")


if __name__ == "__main__":
    main()
