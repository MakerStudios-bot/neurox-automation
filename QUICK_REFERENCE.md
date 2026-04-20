# 📋 Neurox Bot Provisioner - Quick Reference

Cheat sheet para desarrolladores.

## 🚀 Comandos Rápidos

```bash
# Validar configuración
python3 test_config.py

# Ejecutar tests de provisioning
python3 test_provisioner.py

# Iniciar servidor (desarrollo)
uvicorn backend.main:app --reload --port 8000

# Iniciar servidor (producción)
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Ver base de datos
sqlite3 neurox_provisioning.db

# Listar todos los bots
sqlite3 neurox_provisioning.db "SELECT * FROM bots_provisionados;"

# Ver logs de un bot
sqlite3 neurox_provisioning.db "SELECT * FROM logs_provisioning WHERE bot_id = 1;"
```

## 🔌 API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Dashboard HTML |
| GET | `/api/servicios` | Lista de productos + config + prompts |
| POST | `/api/provisionar` | Inicia provisioning (background) |
| GET | `/api/historial` | Historial de bots |
| GET | `/api/bot/{id}` | Estado de un bot |
| GET | `/api/status` | Estado del sistema |

## 📁 Estructura de Archivos Clave

```
backend/
  main.py           ← FastAPI app + endpoints
  provisioner.py    ← Lógica de provisioning
  database.py       ← SQLite operations
  railway_api.py    ← GraphQL client para Railway
  meta_api.py       ← Placeholder para Meta/Instagram

config/
  productos.json    ← Definición de los 5 productos
  prompts.json      ← System prompts personalizables

frontend/
  index.html        ← Dashboard responsivo

test_*.py          ← Scripts de testing
```

## 🎯 Flujo de Provisioning (En Código)

```python
# 1. Usuario envía datos
POST /api/provisionar
{
  "tipo_servicio": "vendedor_ia_pro",
  "nombre_negocio": "Mi Empresa",
  "instagram": "@mi_empresa",
  ...más campos según el tipo...
}

# 2. Backend ejecuta en background:
provisionar_bot(datos, tipo_servicio)

# 3. Pasos en provisioner.py:
# - guardar_bot() → Guarda en BD
# - meta.validar_credenciales_instagram()
# - railway.clonar_proyecto()
# - railway.configurar_variable() → x N variables
# - meta.conectar_webhook()
# - railway.desplegar_servicio()
# - actualizar_bot(estado="listo")

# 4. Usuario ve historial con el bot listo
```

## 🧠 Agregar un Nuevo Producto

### 1. Editar `config/productos.json`

```json
{
  "nuevo_producto": {
    "nombre": "Mi Nuevo Producto",
    "precio": 999000,
    "tipo": "bot",
    "template": "template-name",
    "campos_obligatorios": ["campo1", "campo2"],
    "campos_adicionales": { "campo3": { ... } },
    "capacidades": { "feature1": true, "feature2": false }
  }
}
```

### 2. Editar `config/prompts.json`

```json
{
  "nuevo_producto": {
    "descripcion": "Descripción del producto",
    "sistema": "Prompt del sistema para la IA",
    "instrucciones": ["instrucción 1", "instrucción 2"]
  }
}
```

### 3. Crear template en Railway

- Nombre: `template-name`
- Incluye código base del bot
- Variables de entorno serán inyectadas automático

### 4. Testear

```bash
python3 test_provisioner.py
```

## 🔧 Agregar un Campo Dinámico

El formulario en el frontend es completamente dinámico.

### 1. Actualizar `config/productos.json`

```json
{
  "producto_existente": {
    "campos_obligatorios": ["campo_nuevo", ...otros...],
    "campos_adicionales": {
      "campo_nuevo": {
        "descripcion": "Descripción",
        "tipo": "text|textarea|array"
      }
    }
  }
}
```

### 2. (Opcional) Agregar en `frontend/index.html` → mapeoLabels

```javascript
const mapeoLabels = {
  'campo_nuevo': {
    label: 'Etiqueta del Campo',
    placeholder: 'Placeholder ejemplo',
    type: 'text'
  }
}
```

### 3. Usar en `config/prompts.json`

```json
{
  "producto": {
    "sistema": "...{campo_nuevo}..."
  }
}
```

## 📊 Actualizar la Base de Datos

### Agregar una nueva columna

```python
# En database.py, agregar en inicializar_db():
cursor.execute("""
  ALTER TABLE bots_provisionados
  ADD COLUMN nueva_columna TEXT
""")

# También actualizar campos_permitidos en actualizar_bot():
campos_permitidos = [..., 'nueva_columna']
```

### Limpiar la BD (desarrollo)

```bash
rm neurox_provisioning.db
# Se recreará automático en el próximo inicio
```

## 🔍 Debugging Tips

### Ver todas las variables de un bot

```bash
sqlite3 neurox_provisioning.db
SELECT json_extract(metadata, '$.') FROM bots_provisionados WHERE id=1;
```

### Simular provisioning sin Railway

En `provisioner.py`, comentar los pasos de Railway:

```python
# Paso 3: # Clonar proyecto en Railway
proyecto_clonado_id = "test-project-" + str(random.randint(10000, 99999))
```

### Ver qué datos envía el frontend

En `frontend/index.html`, agregar antes de fetch:

```javascript
console.log('Datos a enviar:', JSON.stringify(datos, null, 2));
```

## 🌍 Campos Disponibles para Cada Producto

### Bot Automático Sin IA
- nombre_negocio*
- rubro*
- instagram*
- contacto_derivacion*

### Bot Automático Con IA
- nombre_negocio*
- rubro*
- instagram*
- tono_respuesta*
- contacto_derivacion*
- servicios (opcional)
- horario_atencion (opcional)

### Vendedor IA Starter
- nombre_negocio*
- rubro*
- instagram*
- tono_venta*
- servicios*
- link_agendamiento*
- contacto_whatsapp*

### Vendedor IA Pro (+ campos de Starter)
- whatsapp_derivacion* (reemplaza contacto_whatsapp)

### Vendedor IA Elite (+ campos de Pro)
- base_clientes_inactivos*

## 🎨 Estilos CSS

Todos los estilos usando **Tailwind CSS** v3.

El HTML está en `frontend/index.html`. Para modificar:

1. Editar clases Tailwind directamente en HTML
2. O configurar Tailwind en `tailwind.config.js` si tienes

Colores principales:
- Fondo: `from-slate-900` a `to-slate-900`
- Acento: `from-blue-400` a `cyan-400`
- Éxito: `green-500`
- Error: `red-500`

## 🔑 Variables de Entorno en Railway

Automáticamente inyectadas:

```
TOKEN_DE_VERIFICACIÓN=neurox_verification_token_123
APP_SECRET=neurox_app_secret_456
CLAVE_API_ANTROPICA=sk-ant-...
CLIENTE_NOMBRE={nombre_negocio}
INSTAGRAM_USERNAME={instagram}
TIPO_SERVICIO={tipo_servicio}
PROMPT_SISTEMA={prompt personalizado}
... más según el cliente ...
```

## 🐞 Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `RAILWAY_API_TOKEN not found` | .env no configurado | `cp .env.example .env` + editar |
| `Port 8000 already in use` | Otra app usa el puerto | `uvicorn ... --port 8001` |
| `Module not found` | Dependencias no instaladas | `pip install -r requirements.txt` |
| `Instagram credentials invalid` | Credenciales falsas | Usar credenciales reales o (en dev) quitar validación |
| `Failed cloning project` | Railway token inválido | Verificar token en .env |

## 📈 Monitoreo

### Health Check

```bash
curl http://localhost:8000/api/status
```

### Logs en Real-Time

```bash
# Terminal 1
uvicorn backend.main:app --reload

# Terminal 2
tail -f <logfile> 2>/dev/null | grep "provisioning\|error"
```

## 🚀 Deploy a Producción

### Con Railway

```bash
# 1. Crear proyecto en Railway
# 2. Conectar GitHub repo
# 3. Configurar variables en Railway dashboard:
RAILWAY_API_TOKEN=...
NEUROX_VENDEDOR_NOMBRE=...
# 4. Railway auto-deploya en cada push

# Ver logs
railway logs
```

### Con Heroku

```bash
heroku login
heroku create mi-app
git push heroku main
```

### Con Docker

```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

**Última actualización**: 2026-04-17  
**Version**: 1.0.0
