"""
Vigía — API backend de la consola de observabilidad multinube.

Endpoints:
  GET  /                     -> estado del servicio (health check)
  GET  /salud                -> health check para el balanceador de carga
  POST /lecturas             -> registra una nueva lectura de región
  GET  /lecturas             -> lista las últimas lecturas
  GET  /lecturas/resumen     -> resumen agregado por proveedor y región
  GET  /docs                 -> documentación interactiva automática (Swagger)

La conexión a la base de datos se inyecta en cada endpoint mediante
Depends(get_session), lo que mantiene el código desacoplado y testeable.
"""
import os
import socket
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select, func

from .database import crear_tablas, get_session
from .models import Lectura, LecturaCrear

app = FastAPI(
    title="Vigía API",
    description="Backend de la consola de observabilidad multinube. "
                "Recibe y consulta lecturas de estado de regiones cloud.",
    version="1.0.0",
)

# --- CORS ---
# El frontend vive en otro dominio (Netlify), así que es una petición de origen
# cruzado. Aquí se autoriza ese origen. En producción se restringe al dominio real.
ORIGENES = os.getenv(
    "CORS_ORIGINS",
    "https://vigia-multicloud.netlify.app,http://localhost:5500,http://127.0.0.1:5500",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def al_iniciar():
    """Al arrancar el servidor, se asegura de que las tablas existan."""
    crear_tablas()


@app.get("/", tags=["Estado"])
def raiz():
    """Estado general del servicio. Incluye el nombre del host que responde,
    útil para comprobar visualmente que el balanceador reparte entre backends."""
    return {
        "servicio": "Vigía API",
        "estado": "operativo",
        "servidor": socket.gethostname(),
    }


@app.get("/salud", tags=["Estado"])
def salud():
    """Endpoint liviano para que el balanceador de carga verifique la salud
    de esta instancia. Debe responder rápido y sin tocar la base de datos."""
    return {"estado": "ok"}


@app.post("/lecturas", response_model=Lectura, status_code=status.HTTP_201_CREATED, tags=["Lecturas"])
def crear_lectura(datos: LecturaCrear, session: Session = Depends(get_session)):
    """Registra una nueva lectura de estado de una región."""
    estados_validos = {"operativo", "degradado", "critico"}
    if datos.estado not in estados_validos:
        raise HTTPException(
            status_code=422,
            detail=f"Estado inválido. Use uno de: {', '.join(sorted(estados_validos))}",
        )
    lectura = Lectura.model_validate(datos)
    session.add(lectura)
    session.commit()
    session.refresh(lectura)
    return lectura


@app.get("/lecturas", response_model=List[Lectura], tags=["Lecturas"])
def listar_lecturas(limite: int = 50, session: Session = Depends(get_session)):
    """Devuelve las últimas lecturas registradas, más recientes primero."""
    limite = max(1, min(limite, 500))  # protege contra consultas gigantes
    consulta = select(Lectura).order_by(Lectura.creada_en.desc()).limit(limite)
    return session.exec(consulta).all()


@app.get("/lecturas/resumen", tags=["Lecturas"])
def resumen(session: Session = Depends(get_session)):
    """Resumen agregado: promedio de latencia y número de lecturas por
    proveedor y región. Demuestra una consulta con GROUP BY sobre la base de datos."""
    consulta = (
        select(
            Lectura.proveedor,
            Lectura.region,
            func.count(Lectura.id).label("total"),
            func.avg(Lectura.latencia_ms).label("latencia_promedio"),
        )
        .group_by(Lectura.proveedor, Lectura.region)
        .order_by(Lectura.proveedor)
    )
    filas = session.exec(consulta).all()
    return [
        {
            "proveedor": f.proveedor,
            "region": f.region,
            "total_lecturas": f.total,
            "latencia_promedio_ms": round(f.latencia_promedio, 1) if f.latencia_promedio else 0,
        }
        for f in filas
    ]
