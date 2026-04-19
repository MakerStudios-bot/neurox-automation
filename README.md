# Neurox Bot Provisioner

Automatización inteligente para provisionar bots y vendedores IA en cuentas de Instagram de clientes.

## Características

- 🤖 Provisioning automático de bots
- 📊 Dashboard para gestionar clientes
- 🚀 Integración con Railway para clonar templates
- 🔐 Manejo seguro de credenciales
- 📱 Soporte para múltiples servicios

## Estructura

```
neurox-automation/
├── backend/          # API FastAPI
├── frontend/         # Dashboard HTML/JavaScript
├── config/           # Configuración y credenciales
├── templates/        # Templates de bots en Railway
└── .env             # Variables de entorno
```

## Instalación

1. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

2. **Configurar variables de entorno:**
```bash
# Editar .env
RAILWAY_API_TOKEN=tu_token_aqui
META_APP_ID=tu_app_id
META_APP_SECRET=tu_app_secret
```

3. **Ejecutar:**
```bash
python backend/main.py
```

Acceder en: http://localhost:3000

## Flujo de Provisioning

1. Usuario ingresa datos del cliente (nombre, Instagram, clave)
2. Selecciona servicio (Bot Automático, Vendedor IA, etc.)
3. Sistema clona template en Railway
4. Configura credenciales de Instagram
5. Conecta a Meta/Facebook
6. Bot queda funcionando en la cuenta del cliente

## Servicios Disponibles

- **Bot Automático Instagram** - $180.000
- **Vendedor IA Starter** - $24.000/mes
- **Vendedor IA Pro** - $55.000/mes
- **Vendedor IA Elite** - $105.000/mes

## APIs

### GET /api/servicios
Retorna lista de servicios disponibles

### POST /api/provisionar
Provisiona un nuevo bot para un cliente

```json
{
  "cliente_nombre": "Juan Pérez",
  "cliente_instagram": "mi_usuario",
  "cliente_clave": "mi_clave",
  "tipo_servicio": "vendedor_ia_pro"
}
```

### GET /api/status
Estado de la aplicación y conexiones
