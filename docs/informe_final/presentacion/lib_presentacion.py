# -*- coding: utf-8 -*-
"""Rellena base.pptx (diapositivas de la presentación de la Unidad 2) con el contenido del informe final."""
import copy
from pptx import Presentation
from pptx.util import Inches
from PIL import Image
from pptx.oxml.ns import qn

prs = Presentation("base.pptx")
SL = list(prs.slides)


def sh(slide, sid):
    for s in slide.shapes:
        if s.shape_id == sid:
            return s
    raise KeyError(sid)


def set_text(shape, paras):
    """Reemplaza el texto conservando el formato: el párrafo i usa como molde el párrafo i del original (o el último)."""
    if isinstance(paras, str):
        paras = [paras]
    txBody = shape.text_frame._txBody
    old = txBody.findall(qn("a:p"))
    for p in old:
        txBody.remove(p)
    for i, t in enumerate(paras):
        tpl = copy.deepcopy(old[min(i, len(old) - 1)])
        runs = tpl.findall(qn("a:r"))
        rpr = copy.deepcopy(runs[0].find(qn("a:rPr"))) if runs and runs[0].find(qn("a:rPr")) is not None else None
        for child in list(tpl):
            if child.tag in (qn("a:r"), qn("a:br"), qn("a:fld")):
                tpl.remove(child)
        r = tpl.makeelement(qn("a:r"), {})
        if rpr is not None:
            r.append(rpr)
        tt = r.makeelement(qn("a:t"), {}); tt.text = t; r.append(tt)
        end = tpl.find(qn("a:endParaRPr"))
        if end is not None:
            end.addprevious(r)
        else:
            tpl.append(r)
        txBody.append(tpl)


def delete(slide, *sids):
    for sid in sids:
        e = sh(slide, sid)._element; e.getparent().remove(e)


def put_image(slide, old_sid, path, mode="fit"):
    """Coloca la imagen en el recuadro de la imagen anterior (ajustada o recortada) y elimina la anterior."""
    old = sh(slide, old_sid)
    L, T, W, H = old.left, old.top, old.width, old.height
    w, h = Image.open(path).size
    if mode == "fit":
        k = min(W / w, H / h); nw, nh = int(w * k), int(h * k)
        pic = slide.shapes.add_picture(path, L + (W - nw) // 2, T + (H - nh) // 2, nw, nh)
    else:
        pic = slide.shapes.add_picture(path, L, T, W, H)
    pic.name = old.name
    old._element.addprevious(pic._element)
    old._element.getparent().remove(old._element)
    return pic


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def move(slide, sid, left=None, top=None, width=None, height=None):
    s = sh(slide, sid)
    if left is not None: s.left = Inches(left)
    if top is not None: s.top = Inches(top)
    if width is not None: s.width = Inches(width)
    if height is not None: s.height = Inches(height)


