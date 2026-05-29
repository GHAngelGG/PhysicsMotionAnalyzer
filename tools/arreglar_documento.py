"""
Arregla la estructura del documento Word del proyecto:
- Renumera secciones (1, 2, 3... en vez de CAPITULO II / III)
- Corrige ortografia (PLANTAMIENTO -> PLANTEAMIENTO)
- Elimina duplicacion de "MARCO TEORICO"
- Agrega seccion "EXTENSIONES Y VALOR AGREGADO" antes de Conclusiones
"""
import sys
from copy import deepcopy

from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DOC = r"C:\Users\josea\OneDrive\Documentos\U\Fisica I\Proyecto Final\Entregables\DocumentoFormal - FisicaI.docx"

print("Abriendo documento...")
doc = Document(DOC)

# ─── 1. Mapeo de reemplazos de texto (exactos) ───
REEMPLAZOS = {
    "PLANTAMIENTO DEL PROBLEMA": "3. PLANTEAMIENTO DEL PROBLEMA",
    "RESUMEN": "1. RESUMEN",
    "INTRODUCCION": "2. INTRODUCCIÓN",
    "HIPOTESIS": "4. HIPÓTESIS",
    "JUSTIFICACION": "5. JUSTIFICACIÓN",
    "OBJETIVOS": "6. OBJETIVOS",
    "CAPITULO II: MARCO TEORICO": "7. MARCO TEÓRICO",
    "FUNDAMENTOS TECNOLOGICOS": "8. FUNDAMENTOS TECNOLÓGICOS",
    "CAPITULO III: METODOLOGIA": "9. METODOLOGÍA",
    "CONCLUSION": "11. CONCLUSIONES",
    "RECOMENDACIONES": "12. RECOMENDACIONES",
    "ANEXO": "13. ANEXOS",
}

# Para reemplazar tenemos que iterar los paragraphs y los runs (Word los divide)
print("Aplicando renumeracion y correcciones...")
cambios = 0
para_a_borrar = []   # paragraphs a borrar (los duplicados)

for i, p in enumerate(doc.paragraphs):
    txt_strip = p.text.strip()

    # Detectar el "MARCO TEORICO" duplicado (el segundo que viene despues
    # del "CAPITULO II: MARCO TEORICO")
    if txt_strip == "MARCO TEORICO":
        # Verificar si el anterior ya es "CAPITULO II: MARCO TEORICO"
        anterior = doc.paragraphs[i-1].text.strip() if i > 0 else ""
        if "MARCO TEORICO" in anterior or "MARCO TEÓRICO" in anterior:
            para_a_borrar.append(p)
            print(f"  - Borrando 'MARCO TEORICO' duplicado en linea {i}")
            continue

    # Aplicar reemplazos exactos
    for original, nuevo in REEMPLAZOS.items():
        if txt_strip == original:
            # Reemplazar conservando el formato del primer run
            if p.runs:
                first_run = p.runs[0]
                # Borrar todos los runs adicionales
                for run in p.runs[1:]:
                    run.text = ""
                first_run.text = nuevo
                cambios += 1
                print(f"  ✓ '{original}' → '{nuevo}'")
            break

# Borrar los paragraphs marcados para eliminar
for p in para_a_borrar:
    p._element.getparent().remove(p._element)

print(f"\n{cambios} renombres aplicados, {len(para_a_borrar)} duplicados borrados.")


# ─── 2. Insertar seccion "EXTENSIONES Y VALOR AGREGADO" antes de CONCLUSIONES ───
print("\nInsertando seccion 'EXTENSIONES Y VALOR AGREGADO'...")

# Encontrar el párrafo "11. CONCLUSIONES"
target_para = None
for p in doc.paragraphs:
    if "CONCLUSIONES" in p.text and p.text.strip().startswith("11"):
        target_para = p
        break

if target_para is None:
    # Fallback: buscar "CONCLUSION" si no se cambio
    for p in doc.paragraphs:
        if p.text.strip() in ("CONCLUSION", "CONCLUSIONES"):
            target_para = p
            break

if target_para is None:
    print("  [!] No se encontro CONCLUSIONES, saltando insercion")
else:
    # Función helper para insertar parrafo ANTES de otro
    def insert_para_before(target, text, style_name=None, bold=False, size=None):
        new_p = target.insert_paragraph_before(text)
        if style_name:
            try:
                new_p.style = doc.styles[style_name]
            except KeyError:
                pass
        for run in new_p.runs:
            if bold:
                run.bold = True
            if size:
                run.font.size = Pt(size)
        return new_p

    # Insertar la sección en orden inverso (porque cada insercion va arriba del target)
    # Por lo que el orden de las llamadas es el orden visual de las líneas

    insert_para_before(target_para, "10. EXTENSIONES Y VALOR AGREGADO",
                       style_name="Heading 1")

    insert_para_before(target_para,
        "Más allá de los requerimientos funcionales mínimos, el sistema "
        "incorpora tres extensiones de valor agregado que lo diferencian "
        "de un sistema básico de medición:")

    insert_para_before(target_para,
        "10.1 Inteligencia Artificial aplicada al rastreo de objetos",
        style_name="Heading 2")
    insert_para_before(target_para,
        "El sistema implementa un algoritmo de seguimiento tipo «lock-on» que, "
        "una vez fijado el objetivo mediante el calibrador visual, utiliza una "
        "heurística de proximidad para descartar detecciones erróneas. Esto "
        "significa que, aunque existan otros objetos del mismo color en el cuadro, "
        "el sistema sigue específicamente al objeto de interés. Adicionalmente, "
        "se aplica un filtro Savitzky-Golay sobre las series de posición para "
        "reducir el ruido de las derivadas numéricas, mejorando significativamente "
        "la precisión del cálculo de velocidad y aceleración instantáneas.")

    insert_para_before(target_para,
        "10.2 Reconocimiento automático del tipo de movimiento",
        style_name="Heading 2")
    insert_para_before(target_para,
        "El módulo classifier.py analiza la aceleración media calculada y la "
        "clasifica automáticamente según umbrales físicos: si el promedio "
        "absoluto de la aceleración es menor a 0.5 m/s² el sistema lo identifica "
        "como MRU; si está dentro de 1.5 m/s² del valor de la gravedad (9.8 m/s²) "
        "lo identifica como Caída Libre; en cualquier otro caso lo clasifica como "
        "MRUV. De esta forma, el usuario no necesita indicar manualmente qué tipo "
        "de movimiento está analizando: el sistema lo deduce de los datos.")

    insert_para_before(target_para,
        "10.3 Aplicación multiplataforma: escritorio + web",
        style_name="Heading 2")
    insert_para_before(target_para,
        "Adicional a la aplicación de escritorio desarrollada en Python, se "
        "construyó una versión web completa en HTML5 y JavaScript puro, alojada "
        "gratuitamente en GitHub Pages. Esta versión funciona desde cualquier "
        "dispositivo móvil sin necesidad de instalación, y puede accederse "
        "escaneando un código QR. De esta manera el sistema es portable y "
        "accesible para cualquier estudiante con un celular y conexión a internet, "
        "ampliando significativamente su utilidad educativa.")

    print("  ✓ Seccion insertada exitosamente")


# ─── 3. Guardar ───
print("\nGuardando documento actualizado...")
doc.save(DOC)
print(f"OK: {DOC}")

# ─── 4. Verificar estructura final ───
print("\n=== ESTRUCTURA FINAL ===")
doc2 = Document(DOC)
for i, p in enumerate(doc2.paragraphs):
    style = p.style.name if p.style else ''
    txt = p.text.strip()
    if 'Heading' in style and txt:
        nivel = style.replace('Heading ', 'H')
        prefix = '  ' * (int(style[-1]) if style[-1].isdigit() else 0)
        print(f'{prefix}[{nivel}] {txt}')
