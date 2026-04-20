# 🚀 Neurox Bot Provisioner - Setup Guide

Guía paso a paso para configurar y ejecutar el sistema completo.

## ✅ Checklist de Instalación

- [ ] Clonar/descargar el proyecto
- [ ] Instalar dependencias Python
- [ ] Configurar variables de entorno
- [ ] Validar configuración
- [ ] Iniciar servidor
- [ ] Acceder al dashboard

## 📥 Paso 1: Preparar el Proyecto

```bash
# Si no lo has hecho, clona el proyecto
git clone <repositorio>
cd neurox-automation

# O simplemente navega a la carpeta existente
cd neurox-automation
```

## 📦 Paso 2: Instalar Dependencias

```bash
# Asegúrate de usar Python 3.9+
python3 --version

# Instala las dependencias
pip install -r requirements.txt
```

Si tienes problemas, instala manualmente:

```bash
pip install fastapi uvicorn python-dotenv httpx pydantic requests aiofiles
```

## 🔑 Paso 3: Configurar Variables de Entorno

Copia el archivo de ejemplo y edítalo:

```bash
cp .env.example .env
```

Luego edita `.env` con tus valores:

```env
RAILWAY_API_TOKEN=tu_token_railway_aqui
NEUROX_VENDEDOR_NOMBRE=Tu Nombre
PORT=8000
```

**Dónde obtener el Railway API Token:**
1. Ve a https://railway.app
2. Inicia sesión
3. Ve a Settings → API Tokens
4. Crea un nuevo token
5. Cópialo a tu `.env`

## ✔️ Paso 4: Validar Configuración

```bash
# Ejecuta el validador de configuración
python3 test_config.py
```

Deberías ver:
```
✓ TEST 1: Validando archivos de configuración
   ✅ productos.json encontrado
   ✅ prompts.json encontrado
   ✅ .env encontrado
... etc ...
   ✅ VALIDACIÓN COMPLETADA
```

Si hay errores, corrige los archivos indicados.

## 🚀 Paso 5: Iniciar el Servidor

```bash
# Opción 1: Modo desarrollo (con auto-reload)
uvicorn backend.main:app --reload --port 8000

# Opción 2: Modo producción
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Deberías ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Application startup complete
```

## 🌐 Paso 6: Acceder al Dashboard

Abre tu navegador y ve a:

```
http://localhost:8000
```

Deberías ver el dashboard de Neurox Bot Provisioner.

## 🧪 Paso 7: Probar el Sistema (Opcional)

En otra terminal, ejecuta:

```bash
python3 test_provisioner.py
```

Esto provisiona 5 bots de prueba y valida todo el sistema.

## 🎯 Primeros Pasos en el Dashboard

### Crear tu Primer Bot

1. **Selecciona un servicio:**
   - Bot Automático Sin IA - $110.000
   - Bot Automático Con IA - $180.000
   - Vendedor IA Starter - $230.000
   - Vendedor IA Pro - $380.000
   - Vendedor IA Elite - $580.000

2. **Completa el formulario dinámico:**
   - Los campos cambian según el servicio seleccionado
   - Todos los campos marcados con * son obligatorios

3. **Haz clic en "Provisionar Bot":**
   - El sistema clona un proyecto en Railway
   - Configura las variables de entorno
   - Conecta el webhook de Instagram
   - Despliega automáticamente

4. **Comprueba el historial:**
   - Click en la pestaña "Historial"
   - Verás el estado de todos los bots provisionados

## 🔍 Verificar que Todo Funciona

### Check 1: Frontend carga correctamente
- [ ] Dashboard visible
- [ ] Botones de servicios funcionan
- [ ] Formulario dinámico cambia según servicio

### Check 2: Backend responde
```bash
# En otra terminal
curl http://localhost:8000/api/servicios
# Deberías ver JSON con lista de servicios
```

### Check 3: Base de datos funciona
```bash
# Ver bots provisionados
sqlite3 neurox_provisioning.db "SELECT * FROM bots_provisionados;"
```

## 🐛 Solución de Problemas

### Error: "RAILWAY_API_TOKEN no está configurado"

Solución:
1. Copia `.env.example` a `.env`
2. Edita `.env` y agrega tu Railway API token
3. Reinicia el servidor

### Error: "ImportError: No module named 'fastapi'"

Solución:
```bash
pip install -r requirements.txt
```

### Error: "Port 8000 already in use"

Solución:
```bash
# Usa un puerto diferente
uvicorn backend.main:app --port 8080

# O matar el proceso que usa el puerto
lsof -i :8000
kill -9 <PID>
```

### El servidor no clona proyectos en Railway

Solución:
1. Verifica que tu Railway API token sea válido
2. Ve a https://railway.app/dashboard y verifica que tengas proyectos
3. Comprueba que los templates existan:
   - mellow-elegance (para bots)
   - radiant-ambition (para vendedores IA)

## 📞 Debugging

### Ver logs del servidor

Los logs aparecen en la terminal donde ejecutaste `uvicorn`.

### Ver base de datos

```bash
# Listar todos los bots
sqlite3 neurox_provisioning.db "SELECT cliente_nombre, estado FROM bots_provisionados;"

# Ver logs de un bot específico
sqlite3 neurox_provisioning.db "SELECT * FROM logs_provisioning WHERE bot_id = 1;"
```

### Test de API

```bash
# Obtener servicios
curl http://localhost:8000/api/servicios

# Obtener historial
curl http://localhost:8000/api/historial

# Obtener estado del sistema
curl http://localhost:8000/api/status
```

## 🎓 Estructura de Carpetas Importante

```
neurox-automation/
├── backend/main.py           ← Servidor FastAPI
├── frontend/index.html       ← Dashboard
├── config/productos.json     ← Definición de productos
├── config/prompts.json       ← System prompts personalizables
├── test_provisioner.py       ← Tests de funcionalidad
├── test_config.py            ← Validador de config
├── .env                      ← Variables de entorno (no en git)
├── .env.example              ← Plantilla de .env
└── neurox_provisioning.db    ← Base de datos (generada automático)
```

## 🚀 Próximos Pasos

Una vez funcionando:

1. **Personaliza los productos** en `config/productos.json`
2. **Ajusta los prompts** en `config/prompts.json`
3. **Configura los templates** en Railway
4. **Agrega autenticación** si es necesario
5. **Despliega en producción** (Railway, Heroku, etc)

## 📞 Soporte

Si tienes problemas:

1. Ejecuta `python3 test_config.py` para validar configuración
2. Revisa los logs en la terminal
3. Consulta el archivo `README.md` para documentación completa
4. Verifica que Railway API token sea válido

---

**¡Listo! Tu Neurox Bot Provisioner está configurado y funcionando. 🎉**

Para más información, ver `README.md`.
