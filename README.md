# Neurox Bot Provisioner

Automatización inteligente para provisionar bots de Instagram con diferentes capacidades (sin IA, con IA, Vendedor IA Starter/Pro/Elite).

## 🚀 Características Principales

- **Dashboard interactivo** con formularios dinámicos según el tipo de bot
- **5 tipos de productos** con configuración independiente:
  - Bot Automático Sin IA (respuestas predefinidas)
  - Bot Automático Con IA (conversación natural)
  - Vendedor IA Starter (calificación básica)
  - Vendedor IA Pro (calificación + follow-up)
  - Vendedor IA Elite (todo + reactivación)
- **Integración Railway** para deployment automático
- **Base de datos SQLite** para historial completo
- **API REST** para automatización externa
- **Testing suite** completa incluida

## 📁 Estructura del Proyecto

```
neurox-automation/
├── backend/
│   ├── main.py              # FastAPI app con todos los endpoints
│   ├── provisioner.py       # Lógica principal de provisioning
│   ├── database.py          # SQLite para historial
│   ├── railway_api.py       # Cliente GraphQL para Railway
│   └── meta_api.py          # Cliente para Instagram/Meta API
├── frontend/
│   └── index.html           # Dashboard responsive con Tailwind
├── config/
│   ├── productos.json       # Definición de todos los productos
│   ├── prompts.json         # System prompts personalizables
│   └── templates.json       # IDs de templates en Railway
├── test_provisioner.py      # Suite de tests de funcionalidad
├── test_config.py           # Validador de configuración
├── .env                     # Variables de entorno
└── neurox_provisioning.db   # Base de datos (se crea automático)
```

## ⚡ Quick Start

### 1. Instalar Dependencias

```bash
cd neurox-automation
pip install fastapi uvicorn python-dotenv httpx
```

### 2. Validar Configuración

```bash
python test_config.py
```

Esto verifica:
- ✅ Archivos de config existen
- ✅ JSON es válido
- ✅ Imports de Python funcionan
- ✅ Directorios están en orden

### 3. Iniciar el Servidor

```bash
uvicorn backend.main:app --reload --port 8000
```

Luego acceder a: **http://localhost:8000**

### 4. (Opcional) Ejecutar Tests

```bash
python test_provisioner.py
```

Esto provisiona 5 bots de prueba y valida todo el sistema.

## 🧪 Testing

### Test de Configuración

Valida que todos los archivos y dependencias estén en orden:

```bash
python test_config.py
```

Output:
```
✓ TEST 1: Validando archivos de configuración
   ✅ productos.json encontrado
   ✅ prompts.json encontrado
   ✅ .env encontrado

✓ TEST 2: Validando config/productos.json
   ✅ JSON válido
   ✅ Productos encontrados: 5
      • bot_automatico_sin_ia: Bot Automático Instagram (Sin IA)
      • bot_automatico_con_ia: Bot Automático Instagram (Con IA)
      ... etc
```

### Test de Provisioning

Prueba el flujo completo para todos los tipos de bots:

```bash
python test_provisioner.py
```

Realiza:
- ✅ Conexión a base de datos
- ✅ Provisiona Bot Sin IA
- ✅ Provisiona Bot Con IA
- ✅ Provisiona Vendedor IA Starter/Pro/Elite
- ✅ Obtiene estado de cada bot
- ✅ Lista historial
- ✅ Genera reporte

## 🎨 Dashboard

El dashboard (`frontend/index.html`) incluye:

### Tab 1: Nuevo Cliente

Formulario dinámico que cambia según el producto seleccionado.

**Productos disponibles:**

1. **Bot Automático Sin IA** - $110.000
   - Campos: nombre_negocio, rubro, instagram, contacto_derivacion
   - Respuestas predefinidas y FAQs

2. **Bot Automático Con IA** - $180.000
   - Campos adicionales: tono_respuesta, servicios, horario_atencion
   - Conversación natural sin venta

3. **Vendedor IA Starter** - $230.000
   - Campos adicionales: tono_venta, link_agendamiento
   - Calificación básica de leads

4. **Vendedor IA Pro** - $380.000
   - Campos adicionales: criterios_calificacion, secuencia_nurturing
   - Follow-up automático y transferencia a WhatsApp

5. **Vendedor IA Elite** - $580.000
   - Campos adicionales: guion_venta, base_clientes_inactivos
   - Reactivación de clientes + optimización mensual

### Tab 2: Historial

Muestra todos los bots provisionados con estado actual:
- Cliente
- Instagram
- Tipo de servicio
- Estado (provisionando, listo, error, etc)
- Fecha de creación

## 🔌 API Endpoints

### GET `/`
Sirve el dashboard HTML

### GET `/api/servicios`
Retorna lista de servicios + configuración + prompts

```json
{
  "ok": true,
  "servicios": {
    "bot_automatico_sin_ia": {
      "nombre": "Bot Automático Instagram (Sin IA)",
      "precio": 110000
    }
  },
  "configuracion": { ... },
  "prompts": { ... }
}
```

### POST `/api/provisionar`
Inicia el provisioning de un nuevo bot (background task)

```json
{
  "tipo_servicio": "bot_automatico_con_ia",
  "nombre_negocio": "Mi Negocio",
  "instagram": "mi_negocio",
  "rubro": "E-commerce",
  "tono_respuesta": "amigable",
  "contacto_derivacion": "+54 9 1234 5678"
}
```

### GET `/api/historial`
Retorna historial de todos los bots provisionados

```json
{
  "ok": true,
  "total": 5,
  "bots": [
    {
      "id": 1,
      "cliente": "Mi Negocio",
      "instagram": "mi_negocio",
      "servicio": "bot_automatico_con_ia",
      "estado": "listo",
      "fecha": "2026-04-17T10:30:00"
    }
  ]
}
```

### GET `/api/bot/{id}`
Estado detallado de un bot específico

### GET `/api/status`
Estado general del sistema

```json
{
  "ok": true,
  "estado": "operacional",
  "railway_conectado": true,
  "servicios_disponibles": 5
}
```

## ⚙️ Configuración de Productos

Archivo: `config/productos.json`

Cada producto define:
- **nombre**: Nombre descriptivo
- **precio**: Precio en pesos
- **tipo**: bot o vendedor_ia
- **template**: Nombre del template en Railway
- **campos_obligatorios**: Lista de campos requeridos
- **campos_adicionales**: Campos opcionales
- **capacidades**: Qué puede hacer el bot
- **herencia**: Pro y Elite heredan de Starter (solo para vendedores IA)

Ejemplo:

```json
{
  "bot_automatico_sin_ia": {
    "nombre": "Bot Automático Instagram (Sin IA)",
    "precio": 110000,
    "tipo": "bot",
    "template": "mellow-elegance",
    "campos_obligatorios": [
      "nombre_negocio",
      "rubro",
      "instagram",
      "contacto_derivacion"
    ],
    "capacidades": {
      "respuestas_predefinidas": true,
      "califica_leads": false
    }
  }
}
```

## 💬 Personalización de Prompts

Archivo: `config/prompts.json`

Los system prompts se personalizan automáticamente:

```json
{
  "bot_automatico_con_ia": {
    "sistema": "Eres un asistente de {nombre_negocio} en Instagram...",
    "instrucciones": [
      "Responde sobre: {servicios}",
      "Mantén tono: {tono_respuesta}",
      "Horario: {horario_atencion}"
    ]
  }
}
```

Variables disponibles para interpolación:
- `{nombre_negocio}` - Nombre del negocio
- `{instagram}` - Usuario Instagram
- `{tono_respuesta}` - Tono de respuesta
- `{tono_venta}` - Tono de venta
- `{servicios}` - Servicios ofrecidos
- `{contacto_derivacion}` - Contacto de derivación
- Y más según el producto...

## 🔄 Flujo de Provisioning

1. **Usuario completa formulario** en el dashboard
2. **Sistema valida datos** según campos_obligatorios
3. **Guarda en BD** con estado "provisionando"
4. **Valida credenciales Instagram** (si requiere)
5. **Clona proyecto en Railway** (basado en template)
6. **Configura variables de entorno**:
   - Datos del cliente
   - Prompts personalizados
   - Credenciales compartidas
7. **Conecta webhook** a Instagram (si aplica)
8. **Despliega en Railway** automáticamente
9. **Actualiza estado** a "listo"

## 📊 Base de Datos

### Tabla: bots_provisionados

```
id                      INTEGER PRIMARY KEY
cliente_nombre          TEXT
cliente_instagram       TEXT UNIQUE
tipo_servicio          TEXT
railway_project_id     TEXT
instagram_id           TEXT
token_acceso           TEXT
estado                 TEXT (provisionando|listo|error_*)
fecha_creacion         TIMESTAMP
fecha_listo            TIMESTAMP
metadata               JSON
```

### Tabla: logs_provisioning

```
id                      INTEGER PRIMARY KEY
bot_id                  INTEGER (FK)
evento                  TEXT
mensaje                 TEXT
fecha                   TIMESTAMP
```

## 🔐 Seguridad

- Contraseñas NO se guardan en BD
- Tokens se almacenan en metadata con acceso restringido
- Variables sensibles en Railway (no en código)
- RAILWAY_API_TOKEN debe estar en .env

## 🛠️ Configurar Variables de Entorno

Crear archivo `.env`:

```env
# Requerido para clonar proyectos en Railway
RAILWAY_API_TOKEN=tu_token_railway_aqui

# Opcional: endpoint de Railway (por defecto es la API pública)
RAILWAY_API_URL=https://api.railway.app/graphql

# Opcional: configuración de Meta (para validación real)
META_APP_ID=tu_app_id
META_APP_SECRET=tu_app_secret
META_BUSINESS_ACCOUNT_ID=tu_account_id

# Opcional: nombre que aparece en el sistema
NEUROX_VENDEDOR_NOMBRE=María

# Puerto para el servidor
PORT=8000
```

## 🚨 Limitaciones Actuales

- Meta API es placeholder (no valida realmente)
- Webhook de Instagram requiere setup manual
- Railway requiere token válido para clonar

## 📝 Próximas Mejoras

- [ ] Integración real con Meta API
- [ ] Dashboard con gráficos
- [ ] Webhooks para notificaciones
- [ ] Sistema de pagos (Stripe)
- [ ] Diferentes niveles de membresía
- [ ] Panel para clientes
- [ ] Analytics y reportes

---

**Versión**: 1.0.0  
**Estado**: Production Ready  
**Última actualización**: 2026-04-17
