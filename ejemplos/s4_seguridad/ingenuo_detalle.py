"""Separa, en las respuestas al prompt ingenuo, los pasos Gherkin del texto de aviso. Se ejecuta desde la raíz."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
sys.stdout.reconfigure(encoding="utf-8")

from ejemplos.s4_seguridad.prompt_hardening import ENDURECIDO, HISTORIA, INGENUO, SENALES, orden_en_criterios
from ejemplos.comun import modelo

PASO = re.compile(r"^\s*(?:\*\*)?(Escenario|Esquema|Dado|Cuando|Entonces|Y|Pero|Característica)\b", re.I)
destino = Path(sys.argv[1])
destino.mkdir(parents=True, exist_ok=True)
resumen = {"Ingenuo": [0, 0], "Endurecido": [0, 0]}
for i in range(3):
    for nombre, plantilla in (("Ingenuo", INGENUO), ("Endurecido", ENDURECIDO)):
        texto = modelo(1500).invoke(plantilla.format(historia=HISTORIA)).text
        (destino / f"{nombre}_{i}.txt").write_text(texto, encoding="utf-8")
        pasos = [l for l in texto.splitlines() if PASO.match(l)]
        en_pasos = [l.strip() for l in pasos if any(s in l.lower() for s in SENALES)]
        script = bool(orden_en_criterios(texto))
        resumen[nombre][0] += script
        resumen[nombre][1] += bool(en_pasos)
        print(f"{nombre} {i + 1}: script={script} | pasos Gherkin={len(pasos)} | señales en pasos={len(en_pasos)}")
        for l in en_pasos:
            print("    ", l)
print("\nVeces que llegó  (criterio del script | solo pasos Gherkin), de 3:")
for nombre, (a, b) in resumen.items():
    print(f"  {nombre:<11} {a} | {b}")
