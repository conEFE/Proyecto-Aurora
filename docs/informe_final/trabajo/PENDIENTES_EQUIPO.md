# Lo que falta para cerrar el Informe Final 1.0 (al 25-11-2026, maestro 1.7-rc)

Todo lo que se podía hacer con el código y el repositorio ya está en el maestro. Lo que queda depende del equipo.
Casi todo se completa **escribiendo en un archivo** y ejecutando **un comando**; el resto está marcado como «a mano».

## Cómo completar

1. Abra `trabajo/pendientes_equipo.json` y llene solo lo que ya tenga (deje `""` en el resto).
2. Pruebe sin tocar nada:

   ```bash
   bash docs/informe_final/herramientas/completar_pendientes.sh --probar
   ```

   Muestra qué se aplicaría y qué sigue faltando.
3. Aplique: el mismo comando sin `--probar`. Respalda el maestro en `respaldos/`, lo actualiza, lo valida y vuelve a
   exportar `trabajo/Proyecto_Aurora_Informe_Final.pdf`.
4. Anote el cambio en el registro de revisiones y en `trabajo/ESTADO_ITERACION.md` (o pídaselo a Claude).

Se puede ejecutar cuantas veces se quiera: lo ya aplicado no se repite y lo vacío no se toca.

## Lista

| # | Qué | Dónde queda en el informe | Cómo | Quién |
|---|---|---|---|---|
| 1 | **Dedicatoria** | Página «Dedicatoria» (hoy en blanco) | `dedicatoria` en el JSON (párrafos separados por una línea en blanco) | Equipo |
| 2 | **Agradecimientos** | Página «Agradecimientos» (hoy en blanco) | `agradecimientos` | Equipo |
| 3 | **Shah et al. (2023)**: datos completos | Lista de referencias (hoy dice «[FALTA INFORMACIÓN…]»); cita del capítulo IV | `referencias` → `"Shah et al. (2023).": "<entrada APA completa>"`. Si la fuente real es otra, también `cita_shah_en_el_texto` | Equipo |
| 4 | **Cifras de GLOBOCAN 2024** (capítulo II, 2.1): cita y referencia | Hoy con marca «[FALTA INFORMACIÓN…]» | `marcas_capitulo_II.globocan`: `cita` y `referencia` (y `frase_corregida` si cambia una cifra) | Equipo |
| 5 | **Plazos GES** (capítulo II): norma oficial vigente | Hoy con marca «[FALTA INFORMACIÓN…]» | `marcas_capitulo_II.ges`: `cita` y `referencia` | Equipo |
| 6 | Título de **2026c** y descripción de **2026b**; fechas de consulta de **OMS 2026**, **NEMA 2026** y **ACR 2025** | Lista de referencias | `referencias` → entrada completa corregida | Equipo |
| 7 | **Desplegar la 2.12.0** en `demo.auroracare.cl` | XIII (versión publicada), XIV | Despliegue habitual (`docs/ESTADO_AWS.md`); luego `despliegue_2_12_0.fecha` | Felipe |
| 8 | **Repetir PC-01 en AWS con la 2.12.0** (25, 50 y 100 usuarios, sobre una copia de la base) | XII: tabla nueva y texto; Tablas de casos de prueba y de resultados; resumen, abstract, XIV y XVI | Método en `evidencias/rendimiento_aws_2026-11-24/README.md`; guardar los JSON en `evidencias/rendimiento_aws_<fecha>/` y copiar el bloque `total` en `pc01_aws_2_12_0`. El texto se escribe solo según cumpla o no (p95 ≤ 3.000 ms con 100) | Felipe / Juan |
| 9 | **Crear la instancia de respaldo del modelo** (`t4g.small`, detenida salvo en demostraciones) y probar el paso al respaldo | X (infraestructura), XIII, XV, XVI | Pasos en `docs/inferencia_remota.md`, sección 5.1; luego `respaldo_inferencia` | Juan / Felipe |
| 10 | Día de la defensa: PC de Juan encendido, sin suspensión, con Tailscale y el servicio arriba; respaldo encendido la víspera | — (operación) | `docs/guia_modelo_juan.md` y sección 5.1 de `docs/inferencia_remota.md` | Juan |
| 11 | **Correcciones del docente** a U1/U2 | Según lo que indique | A mano: pásenselas a Claude con el documento | Equipo + Claude |
| 12 | **A3**: desarrollo del modelo de IA (CNN, datos, entrenamiento, umbrales, 7 intentos) en 10.7.1 | X, 10.7.1 | A mano: reenviar U2 a Claude (sección 3.8) | Claude, con U2 |
| 13 | Confirmar **CU18** y los casos **PI-06 a PS-09\*** (agregados en el informe) | X, XII y anexos | Leer y avisar si algo no corresponde | Equipo |
| 14 | **Etiquetas de versión** v2.10.1 a v2.12.0 en GitHub (hoy la última es v2.10.0) | XIII («Elementos de configuración») | Crearlas y avisar a Claude para actualizar el texto | Felipe |
| 15 | Alerta de presupuesto de AWS ajustada al costo real | XVI (recomendación) | En AWS Billing; avisar a Claude | Felipe |
| 16 | **Lectura final y aceptación** de la versión 1.0 | Todo | Leer el PDF y anotar observaciones | Equipo |

## Qué hace el script con cada resultado de PC-01 (punto 8)

- **Cumple** (p95 ≤ 3 s con 100 usuarios): agrega la tabla y dice que PC-01 se aprueba; el resumen y el abstract
  dicen que el entorno de demostración cumplió la meta tras la optimización; se retira la recomendación de desplegar y
  medir, y queda la de la prueba de estrés y el escaneo activo.
- **No cumple**: agrega la tabla, indica hasta cuántos usuarios se cumple la meta y que hace falta más capacidad; el
  resumen y el abstract informan el nuevo percentil; la recomendación pasa a «dimensionar la capacidad».

Para PC-01 se necesita antes la fecha de despliegue de la 2.12.0 (punto 7).
