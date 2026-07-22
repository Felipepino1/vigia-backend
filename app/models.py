"""
Modelo de datos: representa una lectura de estado de una región cloud.

Cada registro es una medición que el frontend Vigía (o un agente) envía:
qué región, de qué proveedor, con qué latencia y en qué estado se encontraba.
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class LecturaBase(SQLModel):
    """Campos que llegan desde el cliente al registrar una lectura."""
    proveedor: str = Field(index=True, description="AWS, Azure, GCP, etc.")
    region: str = Field(index=True, description="Ej: sa-east-1, brazilsouth")
    latencia_ms: float = Field(description="Latencia p95 medida en milisegundos")
    estado: str = Field(description="operativo, degradado o critico")


class Lectura(LecturaBase, table=True):
    """Tabla real en la base de datos (hereda los campos de arriba y agrega id y fecha)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    creada_en: datetime = Field(default_factory=datetime.utcnow, index=True)


class LecturaCrear(LecturaBase):
    """Esquema de entrada para el endpoint POST (sin id ni fecha, los pone el servidor)."""
    pass
