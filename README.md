# Vigía — Backend API

Backend de la consola de observabilidad multinube. API construida con FastAPI
que recibe lecturas de estado de regiones cloud y las almacena en una base de datos.

## Requisitos
- Python 3.10 o superior

## Cómo ejecutarlo en tu computador (Windows)

Abre una terminal (cmd o PowerShell) dentro de la carpeta `vigia-backend` y ejecuta:

```
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Carga unos datos de ejemplo (opcional pero recomendado para ver algo):

```
py datos_prueba.py
```

Inicia el servidor:

```
uvicorn app.main:app --reload
```

Luego abre en el navegador:

- http://127.0.0.1:8000/          -> estado del servicio
- http://127.0.0.1:8000/docs      -> documentación interactiva (probar la API aquí)
- http://127.0.0.1:8000/lecturas  -> lista de lecturas

Para detener el servidor: Ctrl + C en la terminal.

## Estructura

```
vigia-backend/
├── app/
│   ├── main.py       # la API y sus endpoints
│   ├── models.py     # el modelo de datos (tabla Lectura)
│   └── database.py   # conexión a la base de datos
├── datos_prueba.py   # carga lecturas de ejemplo
├── requirements.txt  # dependencias
└── README.md
```

## Base de datos: local vs. producción

- **En tu PC**: usa SQLite automáticamente (crea un archivo `vigia.db`). No hay que instalar nada.
- **En producción (Azure)**: define la variable de entorno `DATABASE_URL` con la
  cadena de conexión de PostgreSQL. El código detecta el cambio solo, sin modificar nada más.

Ejemplo de la variable en el servidor:
```
DATABASE_URL=postgresql://usuario:clave@host:5432/vigia
```

## Endpoints principales

| Método | Ruta                | Descripción                                  |
|--------|---------------------|----------------------------------------------|
| GET    | `/`                 | Estado del servicio + nombre del host         |
| GET    | `/salud`            | Health check para el balanceador de carga     |
| POST   | `/lecturas`         | Registra una lectura nueva                     |
| GET    | `/lecturas`         | Lista las últimas lecturas                     |
| GET    | `/lecturas/resumen` | Resumen agregado por proveedor y región        |
