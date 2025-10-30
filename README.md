# 🚀 FastAPI Blog API

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.25-red.svg)](https://www.sqlalchemy.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-purple.svg)](https://docs.pydantic.dev/)
[![Tests](https://img.shields.io/badge/Tests-45%2B-success.svg)](tests/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](docker-compose.yml)

API RESTful completa con FastAPI, SQLAlchemy (async), Pydantic v2 y PostgreSQL. Incluye autenticación JWT, soft delete, migraciones con Alembic, y sistema de permisos.

## Características

### Funcionalidades
- ✅ Operaciones asíncronas con SQLAlchemy
- ✅ Autenticación JWT con OAuth2
- ✅ Soft delete en todos los modelos
- ✅ Timestamps automáticos (created_at, updated_at)
- ✅ Relaciones uno a muchos y muchos a muchos
- ✅ Paginación en endpoints de consulta
- ✅ Sistema de permisos (solo el autor puede editar/eliminar)
- ✅ Middleware de timing para medir rendimiento
- ✅ Validaciones con Pydantic v2
- ✅ Migraciones con Alembic
- ✅ Docker y Docker Compose

### Buenas Prácticas Implementadas
- ✅ **Type Hints y Annotated**: Código más legible y type-safe
- ✅ **Singleton Pattern**: Configuración optimizada con `lru_cache`
- ✅ **Connection Pooling**: Gestión eficiente de conexiones a BD
- ✅ **Logging Estructurado**: Sistema de logs centralizado
- ✅ **Excepciones Personalizadas**: Manejo consistente de errores
- ✅ **Constantes Centralizadas**: Valores reutilizables en `constants.py`
- ✅ **Documentación OpenAPI**: Endpoints documentados con descripciones
- ✅ **Lifecycle Management**: Gestión de startup/shutdown
- ✅ **CORS Configurado**: Listo para frontend
- ✅ **Versionado de API**: Prefijo `/api/v1` para futuras versiones

## Estructura del Proyecto

```
fastapi-blog/
├── app/
│   ├── models/          # Modelos SQLAlchemy + Mixins
│   ├── schemas/         # Esquemas Pydantic con validaciones
│   ├── routers/         # Endpoints organizados por recurso
│   ├── middleware/      # Middleware personalizado (timing)
│   ├── utils/           # Utilidades (auth, dependencies)
│   ├── config.py        # Configuración con Pydantic Settings
│   ├── database.py      # Engine y session con pooling
│   ├── constants.py     # Constantes centralizadas
│   ├── exceptions.py    # Excepciones personalizadas
│   ├── logging_config.py # Configuración de logging
│   └── main.py          # Aplicación FastAPI
├── alembic/             # Migraciones incrementales
│   └── versions/        # 001, 002, 003...
├── tests/               # Suite de tests (45+ tests)
├── scripts/             # Scripts de utilidad
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Instalación

### Con Docker (Recomendado)

1. Clonar el repositorio
2. Ejecutar:

```bash
docker-compose up --build
```

La API estará disponible en `http://localhost:8001`

### Sin Docker

1. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno (copiar .env.example a .env)

4. Ejecutar migraciones:
```bash
alembic upgrade head
```

5. Iniciar servidor:
```bash
uvicorn app.main:app --reload
```

## Uso de la API

### Documentación Interactiva

- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

### Flujo de Autenticación

1. Registrar usuario:
```bash
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "username": "usuario",
  "password": "password123",
  "full_name": "Usuario Test"
}
```

2. Login:
```bash
POST /api/v1/auth/login
Form data:
  username: usuario
  password: password123
```

3. Usar el token en headers:
```
Authorization: Bearer <token>
```

## Migraciones con Alembic

### Crear migración inicial:
```bash
alembic revision --autogenerate -m "Initial migration"
```

### Aplicar migraciones:
```bash
alembic upgrade head
```

### Ejemplo: Agregar nuevo campo

1. Modificar modelo en `app/models/models.py`
2. Crear migración:
```bash
alembic revision --autogenerate -m "Add new field"
```
3. Aplicar:
```bash
alembic upgrade head
```

## Endpoints Principales

> **Nota**: Todos los endpoints están bajo el prefijo `/api/v1`

### Autenticación
- `POST /api/v1/auth/register` - Registrar usuario
- `POST /api/v1/auth/login` - Login y obtener token JWT

### Usuarios
- `GET /api/v1/users/me` - Obtener usuario actual (requiere auth)
- `GET /api/v1/users/{user_id}` - Obtener usuario por ID

### Posts
- `GET /api/v1/posts` - Listar posts (con paginación)
- `GET /api/v1/posts/{post_id}` - Obtener post específico
- `POST /api/v1/posts` - Crear post (requiere auth)
- `PUT /api/v1/posts/{post_id}` - Actualizar post (solo autor)
- `DELETE /api/v1/posts/{post_id}` - Eliminar post (solo autor, soft delete)

### Comentarios
- `GET /api/v1/comments/post/{post_id}` - Listar comentarios de un post
- `POST /api/v1/comments` - Crear comentario (requiere auth)
- `DELETE /api/v1/comments/{comment_id}` - Eliminar comentario (solo autor)

## Características Técnicas

### Mixins Reutilizables

- **TimestampMixin**: Agrega `created_at` y `updated_at`
- **SoftDeleteMixin**: Implementa soft delete con `is_deleted` y `deleted_at`

### Relaciones

- **User → Post**: Uno a muchos
- **User → Comment**: Uno a muchos
- **Post → Comment**: Uno a muchos
- **Post ↔ Tag**: Muchos a muchos

### Validaciones Pydantic v2

- Email válido
- Longitud mínima/máxima de campos
- Campos requeridos
- Configuración con `ConfigDict`

### Middleware

- **TimingMiddleware**: Registra el tiempo de respuesta de cada request

## Testing

Para probar la API, puedes usar:
- Swagger UI en `/docs`
- Postman
- curl
- httpie

Ejemplo con curl:
```bash
# Registrar usuario
curl -X POST "http://localhost:8001/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"test","password":"test1234"}'

# Login
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test&password=test1234"
```

## Tecnologías

- FastAPI 0.109.0
- SQLAlchemy 2.0.25 (async)
- Pydantic 2.5.3
- Alembic 1.13.1
- PostgreSQL
- JWT (python-jose)
- Bcrypt (passlib)
