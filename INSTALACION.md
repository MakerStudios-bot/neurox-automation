# Guía de Instalación - Neurox Bot Provisioner

## Requisitos Previos

- Python 3.9+
- Railway API Token
- Meta/Facebook API credentials (opcional para ahora)

## Instalación Rápida

### 1. Instalar dependencias

```bash
cd /Users/macbookpro/neurox-automation
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

El archivo `.env` ya tiene configurado el Railway API Token.

Si necesitas actualizar variables, edita `.env`:

```bash
# Railway
RAILWAY_API_TOKEN=vob05sYMZJt4rjmdZ2sL6oTmfXVqiKVFGFgH3VsFath
RAILWAY_API_URL=https://api.railway.app/graphql

# Meta/Instagram (opcional)
META_APP_ID=tu_app_id
META_APP_SECRET=tu_app_secret
META_BUSINESS_ACCOUNT_ID=tu_business_account_id

# Neurox Config
NEUROX_VENDEDOR_NOMBRE=María
```

### 3. Crear credenciales compartidas en Railway

Edita `config/templates.json` con tus Project IDs de Railway:

```json
{
  "bot_automatico": {
    "railway_project_id": "TU_PROJECT_ID_AQUI"
  },
  "vendedor_ia_starter": {
    "railway_project_id": "TU_PROJECT_ID_AQUI"
  },
  ...
}
```

### 4. Ejecutar el servidor

```bash
python backend/main.py
```

Acceder en: **http://localhost:3000**

## Flujo de Provisioning

```
1. Usuario ingresa datos del cliente en dashboard
   ├─ Nombre
   ├─ Usuario Instagram
   ├─ Clave Instagram
   └─ Tipo de servicio (Bot, Vendedor IA, etc)

2. Sistema valida y clona template en Railway
   ├─ Crea nuevo proyecto
   ├─ Configura variables (compartidas + cliente)
   └─ Conecta a Instagram

3. Bot queda listo en conta del cliente
   └─ Funciona automáticamente
```

## API Endpoints

### `POST /api/provisionar`
Inicia provisioning de un nuevo bot

**Body:**
```json
{
  "cliente_nombre": "Juan Pérez",
  "cliente_instagram": "juanperez_oficial",
  "cliente_clave": "mi_contraseña_segura",
  "tipo_servicio": "vendedor_ia_pro"
}
```

**Response:**
```json
{
  "ok": true,
  "mensaje": "Provisionando Vendedor IA Pro...",
  "cliente": "Juan Pérez",
  "instagram": "juanperez_oficial",
  "servicio": "Vendedor IA Pro"
}
```

### `GET /api/historial`
Obtiene historial de bots provisionados

**Response:**
```json
{
  "ok": true,
  "total": 5,
  "bots": [
    {
      "id": 1,
      "cliente": "Juan Pérez",
      "instagram": "juanperez_oficial",
      "servicio": "vendedor_ia_pro",
      "estado": "listo",
      "fecha": "2026-04-19T18:30:00"
    }
  ]
}
```

### `GET /api/status`
Estado del sistema

**Response:**
```json
{
  "ok": true,
  "estado": "operacional",
  "railway_conectado": true,
  "vendedor_nombre": "María",
  "servicios_disponibles": 4,
  "proyectos_railway": 12
}
```

## Estructura de la BD

SQLite con 2 tablas:

### `bots_provisionados`
- id (PK)
- cliente_nombre
- cliente_instagram (UNIQUE)
- tipo_servicio
- railway_project_id
- instagram_id
- token_acceso
- estado (provisionando, listo, error)
- fecha_creacion
- fecha_listo
- metadata (JSON)

### `logs_provisioning`
- id (PK)
- bot_id (FK)
- evento
- mensaje
- fecha

## Troubleshooting

### Error: "Railway API Error"
- Verifica que RAILWAY_API_TOKEN es válido
- Revisa que tienes permisos en Railway

### Error: "Credenciales de Instagram inválidas"
- Verifica usuario y contraseña
- Instagram podría tener 2FA habilitado

### Bot no funciona después de provisioning
- Revisa logs en BD: `sqlite3 neurox_provisioning.db`
- Verifica variables de entorno en Railway dashboard
- Comprueba que el webhook está conectado

## Desarrollo Futuro

- [ ] Webhook real para Meta/Instagram
- [ ] UI mejorada con real-time updates
- [ ] Estadísticas de bots activos
- [ ] Auto-restart de servicios fallidos
- [ ] Integración con Slack/Email para notificaciones
