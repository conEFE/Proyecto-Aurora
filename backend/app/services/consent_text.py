"""Texto de consentimiento informado vigente.

Cada versión es inmutable: si el texto cambia, se agrega una versión nueva (y su migración) y la anterior
queda en la BD para saber qué aceptó cada paciente. La migración c1d4f2a8e910 guarda una copia de la v1;
un test verifica que ambas coincidan.
"""

CONSENT_TEXT_VERSION = "2026-11-v1"

CONSENT_TEXT_BODY = """\
CONSENTIMIENTO INFORMADO PARA EL TRATAMIENTO DE DATOS PERSONALES Y DE SALUD
Plataforma Aurora de apoyo a la detección temprana y priorización de casos sospechosos de cáncer de mama

1. Responsable. El establecimiento de salud que la atiende es responsable del tratamiento de sus datos. Puede \
contactarlo por los canales de atención del establecimiento para cualquier consulta o solicitud sobre sus datos.

2. Datos que se tratan. Datos de identificación (RUT, nombre, fecha de nacimiento y sexo), antecedentes \
clínicos relevantes (antecedentes familiares y personales de cáncer de mama, síntomas y BI-RADS informado) e \
imágenes mamarias (mamografía, ecografía o resonancia). Los datos de salud son datos sensibles.

3. Finalidad. Apoyar la priorización (triage) y la revisión médica de su caso. La plataforma usa reglas y un \
sistema de inteligencia artificial como apoyo: ninguna decisión se toma solo de forma automatizada, porque un \
médico revisa, puede corregir y firma el resultado. Sus datos no se usan para otros fines ni se ceden a terceros \
sin una base legal.

4. Seguridad. El acceso está limitado al personal autorizado según su función y queda registrado. Las imágenes \
se guardan cifradas y los reportes identifican el caso con un código anónimo.

5. Conservación. Los datos forman parte de su ficha clínica y se conservan por el plazo que exige la ley \
(Ley 20.584, al menos 15 años). Cumplido el plazo, se eliminan o se anonimizan.

6. Alojamiento. Los datos pueden alojarse en servidores de un proveedor de nube, incluso fuera de Chile, con \
contratos que garantizan un nivel de protección adecuado y cifrado.

7. Sus derechos. Puede pedir acceso a sus datos, su rectificación, su supresión o bloqueo, oponerse a su \
tratamiento y solicitar una copia en formato electrónico (portabilidad). La respuesta se entrega en un plazo de \
30 días corridos. Cuando la ley obligue a conservar la ficha clínica, la supresión se reemplaza por el bloqueo \
de los datos.

8. Retiro del consentimiento. Puede retirar este consentimiento en cualquier momento, sin expresión de causa. \
El retiro impide registrar nuevos casos e imágenes en la plataforma, pero no afecta la licitud del tratamiento \
anterior ni la obligación de conservar la ficha clínica.

Declaro haber sido informada o informado de lo anterior y autorizo el tratamiento de mis datos personales y de \
salud para la finalidad descrita (Ley 19.628 y Ley 21.719)."""
