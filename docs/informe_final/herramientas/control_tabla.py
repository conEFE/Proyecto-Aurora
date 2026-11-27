# -*- coding: utf-8 -*-
import sys,re
from xml.sax.saxutils import escape
p=sys.argv[1]+'/word/document.xml'; x=open(p,encoding='utf-8').read()
def setrow(label,col2,col3):
    i=x.find('<w:t>%s</w:t>'%escape(label)); assert i>0 and x.count('<w:t>%s</w:t>'%escape(label))==1,label
    s=x.rfind('<w:tr>',0,i); e=x.find('</w:tr>',i)+7; row=x[s:e]
    ts=re.findall(r'<w:t>[^<]*</w:t>',row); assert len(ts)==3,(label,ts)
    row2=row.replace(ts[1],'<w:t>%s</w:t>'%escape(col2),1)
    row2=row2.replace(ts[2],'<w:t>%s</w:t>'%escape(col3),1)
    return x[:s]+row2+x[e:]
x=setrow('III. Levantamiento de requerimientos','Instrumentos de levantamiento incorporados; HU01–HU12 integradas con prioridades MoSCoW aprobadas (HU09–HU12 aprobadas el 23-11-2026); HU08 reformulada como necesidad funcional; criterios de HU08–HU12 en estado propuesto.','Pendiente: validar criterios de aceptación HU01–HU12 con evidencia; completar RNF medibles y matriz de trazabilidad HU/RF/RNF/endpoint/entidad/prueba.')
x=setrow('VI. Metodología de trabajo','Redacción inicial en v0.4: Scrumban como evolución del enfoque híbrido de Unidad 1, comparación ponderada, línea base del cronograma con figura, roles, matriz RACI actualizada y plan de recursos por categoría.','Pendiente: confirmar con el equipo la RACI actualizada; contrastar métricas de flujo con registros de GitHub Projects; verificar con Unidad 2 la clave bibliográfica de su informe; estado real del cronograma en capítulo XV.')
x=setrow('VII. Definición de arquitectura TI','No redactado. Antecedentes en Unidad 1 (arquitectura de aplicaciones e infraestructura) y Unidad 2.','Redactar conforme a plantilla; distinguir arquitectura planificada de la desplegada.')
x=setrow('VIII. Arquitectura empresarial','No redactado. Antecedentes en Unidad 1 (estructura organizacional y procesos de negocio).','Redactar sin atribuir a la institución de referencia procesos internos no documentados.')
old='Registro interno de trabajo para la versión 0.3 del documento maestro.'
assert x.count(old)==1; x=x.replace(old,'Registro interno de trabajo para la versión 0.4 del documento maestro (23-11-2026).')
open(p,'w',encoding='utf-8').write(x); print('ok')
