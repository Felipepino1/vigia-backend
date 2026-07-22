"""
Carga unas lecturas de ejemplo en la base de datos, para poder ver
los endpoints de consulta funcionando con datos reales.

Uso:  python datos_prueba.py
(el servidor NO necesita estar corriendo; escribe directo en la base)
"""
from app.database import crear_tablas, engine
from app.models import Lectura
from sqlmodel import Session

EJEMPLOS = [
    ("AWS",   "sa-east-1",              84.0,  "operativo"),
    ("AWS",   "us-east-1",             126.0,  "operativo"),
    ("Azure", "brazilsouth",           197.0,  "degradado"),
    ("Azure", "eastus",                 94.0,  "operativo"),
    ("GCP",   "southamerica-west1",     41.0,  "operativo"),
    ("GCP",   "us-central1",           118.0,  "operativo"),
    ("AWS",   "sa-east-1",              88.0,  "operativo"),
    ("Azure", "brazilsouth",           240.0,  "critico"),
]

crear_tablas()
with Session(engine) as session:
    for proveedor, region, latencia, estado in EJEMPLOS:
        session.add(Lectura(
            proveedor=proveedor, region=region,
            latencia_ms=latencia, estado=estado,
        ))
    session.commit()

print(f"Cargadas {len(EJEMPLOS)} lecturas de ejemplo en la base de datos.")
print("Ahora inicia el servidor y visita http://127.0.0.1:8000/lecturas")
