# 💰 API Revenue Portfolio

Sistema de gestión financiera personal - API REST para control de ingresos, gastos y billeteras digitales.

## 📋 Descripción

API REST construida con Django y Django REST Framework que permite a los usuarios gestionar sus finanzas personales mediante billeteras virtuales, registro de ingresos y seguimiento de gastos.

## 🎯 Características

- ✅ Autenticación JWT
- ✅ Gestión de usuarios
- ✅ Múltiples billeteras por usuario
- ✅ Transferencia entre billeteas
- ✅ Registro de ingresos
- ✅ Seguimiento de gastos
- ✅ Panel de administración
- ✅ Filtrado por billetera
- ✅ Actualización de balance automática
- ✅ Dashboard 
- ✅ Dockerizado con Docker Compose


## 🛠️ Tecnologías

- Python 3.12
- Django 5.1
- Django REST Framework
- PostgreSQL
- JWT Authentication
- Docker & Docker Compose

## 📦 Instalación

### 1. Clonar el repositorio

### 2. Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto:
```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS= *

# Database
POSTGRES_DB=revenue_portfolio_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

### 3. Levantar los servicios con Docker Compose
```bash
docker-compose up --build
```

### 3. Crear superusuario (admin)
```bash
docker-compose exec web python manage.py createsuperuser
```

### 4. Acceder a la aplicación
La API estará disponible en: `http://localhost:8000`
Panel de administración: `http://localhost:8000/admin/`

### Comandos útiles de Docker
```bash
# Ver logs
docker-compose logs -f

# Ver logs solo del servicio web
docker-compose logs -f web

# Detener servicios
docker-compose down

# Detener y eliminar volúmenes (borra la base de datos)
docker-compose down -v

# Reiniciar un servicio específico
docker-compose restart web

# Acceder a la shell de Django
docker-compose exec web python manage.py shell

# Ejecuta migraciones
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Acceder a PostgreSQL
docker-compose exec db psql -U postgres -d revenue_portfolio_db
```

## 📁 Estructura del Proyecto
```
API_revenue_portfolio/
├── API_revenue_portfolio/     # Configuración principal
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/                     # App de usuarios
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── wallets/                   # App de billeteras
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── expenses/                  # App de gastos
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── revenue/                   # App de ingresos
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── docker-compose.yml         # Configuración de Docker
├── Dockerfile                 # Imagen de Docker
├── requirements.txt           # Dependencias Python
├── .env                       # Variables de entorno (crear)
├── .gitignore
└── manage.py
```

## 📊 Cómo Funciona

## 1. **Users (Usuarios/Clientes)**

Cada usuario se registra con nombre, email y contraseña. Cada usuario puede tener múltiples billeteras, ingresos y gastos.

### Registro
- **Endpoint:** `/users/register/`
- **Método:** `POST`
- **Body:**
```json
{
  "username": "juan",
  "email": "juan@example.com",
  "password": "pass123"
}
```
- **Respuesta:**
```json
{
  "message": "User created successfully"
}
```

### Login
- **Endpoint:** `/users/login/`
- **Método:** `POST`
- **Body:**
```json
{
  "username": "juan",
  "password": "pass123"
}
```
- **Respuesta:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Refrescar token
- **Endpoint:** `/users/token/refresh/`
- **Método:** `POST`
- **Body:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Ver perfil
- **Endpoint:** `/users/me/`
- **Método:** `GET`
- **Header:** `Authorization: Bearer <access_token>`
- **Respuesta:**
```json
{
  "id": 1,
  "name": "juan",
  "email": "juan@example.com",
  "wallets": [
    {"id": 1, "name": "Efectivo"},
    {"id": 2, "name": "Banco"}
  ]
}
```

## 2. **Wallets (Billeteras)**

Las billeteras almacenan el balance del usuario. Pueden crear múltiples billeteras para organizar su dinero (efectivo, banco, ahorros, etc.).

### Crear billetera
- **Endpoint:** `/wallets/`
- **Método:** `POST`
- **Header:** `Authorization: Bearer <token>`
- **Body:**
```json
{
  "name": "Efectivo",
  "description": "Dinero en efectivo",
  "balance": 1000.00
}
```

### Listar mis billeteras
- **Endpoint:** `/wallets/`
- **Método:** `GET`
- **Header:** `Authorization: Bearer <token>`

### Ver billetera específica
- **Endpoint:** `/wallets/{id}/`
- **Método:** `GET`
- **Header:** `Authorization: Bearer <token>`

### Actualizar billetera
- **Endpoint:** `/wallets/{id}/`
- **Método:** `PATCH`
- **Header:** `Authorization: Bearer <token>`
- **Body:**
```json
{
  "name": "Efectivo Principal",
  "description": "Actualizada"
}
```

### Agregar saldo manualmente
- **Endpoint:** `/wallets/{id}/add_balance/`
- **Método:** `POST`
- **Header:** `Authorization: Bearer <token>`
- **Body:**
```json
{
  "amount": 500
}
```

### Transferir saldo entre billeteras
- **Endpoint:** `/wallets/{id}/transfer/`
- **Método:** `POST`
- **Header:** `Authorization: Bearer <token>`
- **Body:**
```json
{
  "to_wallet": 2,
  "amount": 10.00,
  "description": "Ahorro mensual"
}
```

### Ver historial de transferencias
- **Endpoint:** `/wallets/{id}/transfers/`
- **Método:** `GET`
- **Header:** `Authorization: Bearer <token>`

### Eliminar billetera
- **Endpoint:** `/wallets/{id}/`
- **Método:** `DELETE`
- **Header:** `Authorization: Bearer <token>`
- **Query Params:** `?force=true` (elimina también expenses asociados)

## 3. **Revenue (Ingresos)**

Registra los ingresos del usuario. Al crear un ingreso, **automáticamente suma el monto a la billetera** seleccionada.

### Crear ingreso
- **Endpoint:** `/revenue/`
- **Método:** `POST`
- **Header:** `Authorization: Bearer <token>`
- **Body:**
```json
{
  "wallet": 1,
  "name": "Salario",
  "description": "Pago mensual",
  "amount": 2000.00,
  "revenue_date": "2025-01-01"
}
```

### Listar ingresos
- **Endpoint:** `/revenue/`
- **Método:** `GET`
- **Header:** `Authorization: Bearer <token>`
- **Query Params:** `?wallet_id=1` (filtrar por billetera)

### Actualizar ingreso
- **Endpoint:** `/revenue/{id}/`
- **Método:** `PATCH`
- **Header:** `Authorization: Bearer <token>`
- **Body:**
```json
{
  "amount": 2100.00
}
```
> ⚠️ **Nota:** Al actualizar el monto, se ajusta automáticamente el balance de la billetera.

### Eliminar ingreso
- **Endpoint:** `/revenue/{id}/`
- **Método:** `DELETE`
- **Header:** `Authorization: Bearer <token>`
> ⚠️ **Nota:** Al eliminar, se resta el monto del balance de la billetera.

## 4. **Expenses (Gastos)**

Registra los gastos del usuario. Al crear un gasto, **automáticamente descuenta el monto de la billetera** seleccionada.

### Crear gasto
- **Endpoint:** `/expenses/`
- **Método:** `POST`
- **Header:** `Authorization: Bearer <token>`
- **Body:**
```json
{
  "wallet": 1,
  "name": "Supermercado",
  "description": "Compras del mes",
  "amount": 200.00,
  "expense_date": "2025-01-15"
}
```
- **Respuesta de error si saldo insuficiente:**
```json
{
  "error": "Insufficient balance"
}
```

### Listar gastos
- **Endpoint:** `/expenses/`
- **Método:** `GET`
- **Header:** `Authorization: Bearer <token>`
- **Query Params:** `?wallet_id=1` (filtrar por billetera)

### Actualizar gasto
- **Endpoint:** `/expenses/{id}/`
- **Método:** `PATCH`
- **Header:** `Authorization: Bearer <token>`
- **Body:**
```json
{
  "name": "Supermercado Actualizado",
  "amount": 250.00
}
```
> ⚠️ **Nota:** Al actualizar el monto, se ajusta automáticamente el balance de la billetera.

### Eliminar gasto
- **Endpoint:** `/expenses/{id}/`
- **Método:** `DELETE`
- **Header:** `Authorization: Bearer <token>`
> ⚠️ **Nota:** Al eliminar, se devuelve el monto al balance de la billetera.

## 5. **Dashboard**

### Dashboard completo del año actual
- **Endpoint:** `/users/dashboard/`
- **Método:** `GET`
- **Header:** `Authorization: Bearer <token>`

### Dashboard de un año específico
- **Endpoint:** `/users/dashboard/?year=2024`
- **Método:** `GET`
- **Header:** `Authorization: Bearer <token>`

### Dashboard de un mes específico
- **Endpoint:** `/users/dashboard/?year=2024&month=1`
- **Método:** `GET`
- **Header:** `Authorization: Bearer <token>`

## 6. **Admin Panel (Solo Administradores)**

Endpoints especiales para administradores del sistema.

### Listar todos los usuarios
- **Endpoint:** `/users/admin/`
- **Método:** `GET`
- **Header:** `Authorization: Bearer <admin_token>`
- **Requiere:** `is_staff=True`

### Eliminar usuario
- **Endpoint:** `/users/admin/{id}/`
- **Método:** `DELETE`
- **Header:** `Authorization: Bearer <admin_token>`
- **Requiere:** `is_staff=True`

### Cambiar contraseña de usuario
- **Endpoint:** `/users/admin/{id}/change-password/`
- **Método:** `POST`
- **Header:** `Authorization: Bearer <admin_token>`
- **Requiere:** `is_staff=True`
- **Body:**
```json
{
  "new_password": "newpass123"
}
```

## 💡 Ejemplo de Uso Real

### Caso: Juan gestiona sus finanzas mensuales

#### **Día 1: Crea sus billeteras**
```bash
# Crea billetera para efectivo
POST /wallets/
Authorization: Bearer TOKEN_ABC123
{
  "name": "Efectivo",
  "description": "Dinero en cartera",
  "balance": 500.00
}
# Response: {"id": 1, "name": "Efectivo", "description": "Dinero en cartera", "balance": "500.00"}

# Crea billetera bancaria
POST /wallets/
Authorization: Bearer TOKEN_ABC123
{
  "name": "Banco Nacional",
  "description": "Cuenta de ahorros",
  "balance": 5000.00
}
# Response: {"id": 2, "name": "Banco Nacional", "description": "Cuenta de ahorros", "balance": "5000.00"}
```

#### **Día 5: Recibe su salario**
```bash
# Registra ingreso de salario
POST /revenue/
Authorization: Bearer TOKEN_ABC123
{
  "wallet": 2,
  "name": "Salario Enero",
  "description": "Pago mensual empresa XYZ",
  "amount": 3000.00,
  "revenue_date": "2025-01-05"
}
# ✅ Balance de "Banco Nacional" automáticamente: $5,000 + $3,000 = $8,000.00
```

#### **Día 7: Retira efectivo del banco**
```bash
# Registra gasto en banco (retiro ATM)
POST /expenses/
Authorization: Bearer TOKEN_ABC123
{
  "wallet": 2,
  "name": "Retiro ATM",
  "description": "Efectivo para la semana",
  "amount": 300.00,
  "expense_date": "2025-01-07"
}
# ✅ Balance "Banco Nacional": $8,000 - $300 = $7,700.00

## 🔒 Seguridad
- 🔐 Autenticación JWT con tokens de acceso y refresh
- 👤 Cada usuario solo puede ver/modificar sus propios datos
- 🛡️ Validación de permisos en cada endpoint
- 🔑 Contraseñas hasheadas (en producción usar `make_password`)
- 👮 Panel de admin protegido con `IsAdminUser`

## 🧪 Testing con Docker
```bash
# Probar endpoints con curl
curl -X POST http://localhost:8000/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"test123"}'

# O usar herramientas como Postman, Insomnia o Thunder Client (VSCode)
```

## 🚀 Despliegue

Para producción, recuerda:
1. Cambiar `DEBUG=False` en `.env`
2. Configurar `ALLOWED_HOSTS` apropiadamente
3. Usar una `SECRET_KEY` segura
4. Configurar HTTPS
5. Usar un servidor WSGI como Gunicorn
6. Configurar un proxy reverso (Nginx)
