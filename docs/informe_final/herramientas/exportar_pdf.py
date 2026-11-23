# -*- coding: utf-8 -*-
"""Exporta el maestro a PDF con LibreOffice, actualizando antes la tabla de contenido, los índices y los campos.
Uso: python3 exportar_pdf.py <entrada.docx> <salida.pdf>
No modifica el DOCX (se abre en modo oculto y solo se exporta)."""
import os, subprocess, sys, tempfile, time, uno
from com.sun.star.beans import PropertyValue

def prop(n, v):
    p = PropertyValue(); p.Name = n; p.Value = v; return p

src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
profile = tempfile.mkdtemp(prefix="lo_profile_")
port = 2002 + os.getpid() % 1000
proc = subprocess.Popen(["soffice", "--headless", "--norestore", "--nologo", "-env:UserInstallation=file://" + profile,
                         "--accept=socket,host=127.0.0.1,port=%d;urp;" % port],
                        env=dict(os.environ, SAL_USE_VCLPLUGIN="svp"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
ctx = None
local = uno.getComponentContext()
resolver = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
for _ in range(60):
    try:
        ctx = resolver.resolve("uno:socket,host=127.0.0.1,port=%d;urp;StarOffice.ComponentContext" % port); break
    except Exception:
        time.sleep(1)
if ctx is None:
    proc.kill(); sys.exit("No se pudo conectar con LibreOffice")
desktop = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
doc = desktop.loadComponentFromURL(uno.systemPathToFileUrl(src), "_blank", 0, (prop("Hidden", True),))
for _ in range(2):  # dos pasadas: los números de página cambian al crecer los índices
    idx = doc.getDocumentIndexes()
    for i in range(idx.getCount()):
        idx.getByIndex(i).update()
    doc.getTextFields().refresh()
    doc.refresh()
print("índices:", doc.getDocumentIndexes().getCount())
doc.storeToURL(uno.systemPathToFileUrl(dst), (prop("FilterName", "writer_pdf_Export"),))
doc.close(True)
try:
    desktop.terminate()
except Exception:
    pass
proc.wait(timeout=60)
print("ok", dst)
