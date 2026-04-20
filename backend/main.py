"""
Neurox Bot Provisioner - Automatiza instalación completa de bots para clientes
"""
import os
import sys
import asyncio
import httpx
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from dotenv import load_dotenv
import json

# Agregar backend al path para imports
sys.path.insert(0, str(Path(__file__).parent))

# Cargar .env desde la raíz del proyecto
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from provisioner import provisionar_bot, obtener_estado_provisioning
from database import obtener_todos_bots, obtener_ruta_webhook, registrar_ruta_webhook, obtener_todas_rutas_webhook
from railway_api import railway

# Cargar configuraciones de productos
CONFIG_PATH = Path(__file__).parent.parent / "config"
with open(CONFIG_PATH / "productos.json") as f:
    PRODUCTOS_CONFIG = json.load(f)
with open(CONFIG_PATH / "prompts.json") as f:
    PROMPTS_CONFIG = json.load(f)

app = FastAPI(title="Neurox Bot Provisioner", version="1.0.0")

# Configuración
NEUROX_VENDEDOR_NOMBRE = os.getenv("NEUROX_VENDEDOR_NOMBRE", "María")

# Servir archivos estáticos del frontend
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

SERVICIOS = {
    "bot_automatico_sin_ia": {
        "nombre": "Bot Automático Instagram (Sin IA)",
        "precio": 110000,
        "descripcion": "Respuestas predefinidas, FAQs y precios",
    },
    "bot_automatico_con_ia": {
        "nombre": "Bot Automático Instagram (Con IA)",
        "precio": 180000,
        "descripcion": "IA personalizada para tu marca, responde como tú",
    },
    "vendedor_ia_starter": {
        "nombre": "Vendedor IA Starter",
        "precio": 230000,
        "descripcion": "Agente IA para negocios que recién empiezan a vender por DM",
    },
    "vendedor_ia_pro": {
        "nombre": "Vendedor IA Pro",
        "precio": 380000,
        "descripcion": "Pipeline completo con seguimiento y calificación automática de leads",
    },
    "vendedor_ia_elite": {
        "nombre": "Vendedor IA Elite",
        "precio": 580000,
        "descripcion": "Solución completa para alto volumen de ventas por Instagram",
    },
}

MEMBRESIAS = {
    "bot_starter": {
        "nombre": "Membresía Bot Starter",
        "precio": 24000,
        "tipo": "mensual",
        "conversaciones_max": 500,
        "caracteristicas": ["500 conversaciones/mes", "Soporte WhatsApp", "1 perfil Instagram"]
    },
    "bot_pro": {
        "nombre": "Membresía Bot Pro",
        "precio": 55000,
        "tipo": "mensual",
        "conversaciones_max": 1500,
        "caracteristicas": ["1.500 conversaciones/mes", "IA personalizada", "Reportes mensuales"]
    },
    "bot_full": {
        "nombre": "Membresía Bot Full",
        "precio": 105000,
        "tipo": "mensual",
        "conversaciones_max": None,
        "caracteristicas": ["Conversaciones ilimitadas", "Mantenimiento activo", "Soporte 24/7"]
    },
    "vendedor_starter": {
        "nombre": "Membresía Vendedor Starter",
        "precio": 55000,
        "tipo": "mensual",
        "conversaciones_max": 500,
        "caracteristicas": ["500 conversaciones/mes", "Soporte WhatsApp", "1 perfil Instagram"]
    },
    "vendedor_pro": {
        "nombre": "Membresía Vendedor Pro",
        "precio": 105000,
        "tipo": "mensual",
        "conversaciones_max": 1500,
        "caracteristicas": ["1.500 conversaciones/mes", "Reportes mensuales", "Optimización del agente"]
    },
    "vendedor_elite": {
        "nombre": "Membresía Vendedor Elite",
        "precio": 160000,
        "tipo": "mensual",
        "conversaciones_max": None,
        "caracteristicas": ["Conversaciones ilimitadas", "Soporte 24/7", "Mantenimiento activo"]
    },
}

@app.get("/")
async def root():
    """Sirve el dashboard principal"""
    dashboard_path = Path(__file__).parent.parent / "frontend" / "index.html"
    if dashboard_path.exists():
        return FileResponse(dashboard_path)
    return JSONResponse({"error": "Dashboard not found"})

@app.get("/api/servicios")
async def listar_servicios():
    """Retorna lista de servicios con configuración completa"""
    return JSONResponse({
        "ok": True,
        "servicios": SERVICIOS,
        "configuracion": PRODUCTOS_CONFIG,
        "membresias": MEMBRESIAS,
        "prompts": PROMPTS_CONFIG
    })

@app.post("/api/provisionar")
async def provisionar_nuevo_bot(request: Request, background_tasks: BackgroundTasks):
    """
    Inicia el provisioning de un nuevo bot.
    Valida según la configuración del producto.
    Corre en background y configura todo automáticamente.
    """
    try:
        data = await request.json()

        tipo_servicio = data.get("tipo_servicio", "").strip()

        # Validar tipo de servicio
        if tipo_servicio not in SERVICIOS:
            return JSONResponse(
                {"ok": False, "error": "Tipo de servicio no válido"},
                status_code=400
            )

        # Obtener configuración del producto
        config_producto = PRODUCTOS_CONFIG.get(tipo_servicio, {})
        campos_obligatorios = config_producto.get("campos_obligatorios", [])

        # Validar campos obligatorios
        for campo in campos_obligatorios:
            if not data.get(campo, "").strip():
                return JSONResponse(
                    {"ok": False, "error": f"Falta campo obligatorio: {campo}"},
                    status_code=400
                )

        # Validar credenciales de Meta
        if not data.get("access_token_meta", "").strip():
            return JSONResponse(
                {"ok": False, "error": "Falta el Access Token de Instagram (Meta)"},
                status_code=400
            )
        if not data.get("instagram_business_account_id", "").strip():
            return JSONResponse(
                {"ok": False, "error": "Falta el Instagram Business Account ID"},
                status_code=400
            )

        servicio = SERVICIOS[tipo_servicio]

        # Dispara provisioning en background
        background_tasks.add_task(
            provisionar_bot,
            data,
            tipo_servicio
        )

        return JSONResponse({
            "ok": True,
            "mensaje": f"Provisionando {servicio['nombre']}...",
            "cliente": data.get("nombre_negocio") or data.get("cliente_nombre"),
            "servicio": servicio['nombre'],
            "tipo": config_producto.get("tipo")
        })

    except Exception as e:
        print(f"❌ Error: {e}")
        return JSONResponse(
            {"ok": False, "error": str(e)},
            status_code=500
        )

@app.get("/api/historial")
async def obtener_historial():
    """Retorna historial de bots provisionados"""
    try:
        bots = obtener_todos_bots(limite=50)

        return JSONResponse({
            "ok": True,
            "total": len(bots),
            "bots": [
                {
                    "id": bot["id"],
                    "cliente": bot["cliente_nombre"],
                    "instagram": bot["cliente_instagram"],
                    "servicio": bot["tipo_servicio"],
                    "estado": bot["estado"],
                    "fecha": bot["fecha_creacion"],
                }
                for bot in bots
            ]
        })

    except Exception as e:
        return JSONResponse(
            {"ok": False, "error": str(e)},
            status_code=500
        )

@app.get("/api/bot/{bot_id}")
async def obtener_estado_bot(bot_id: int):
    """Obtiene el estado detallado de un bot específico"""
    try:
        estado = await obtener_estado_provisioning(bot_id)

        if "error" in estado:
            return JSONResponse(
                {"ok": False, "error": estado["error"]},
                status_code=404
            )

        return JSONResponse({
            "ok": True,
            "bot": estado
        })

    except Exception as e:
        return JSONResponse(
            {"ok": False, "error": str(e)},
            status_code=500
        )

@app.get("/api/status")
async def status():
    """Retorna estado de la aplicación y conexiones"""
    try:
        # Verificar Railway
        proyectos = await railway.obtener_proyectos()
        railway_ok = len(proyectos) > 0

        return JSONResponse({
            "ok": True,
            "estado": "operacional",
            "railway_conectado": railway_ok,
            "vendedor_nombre": NEUROX_VENDEDOR_NOMBRE,
            "servicios_disponibles": len(SERVICIOS),
            "proyectos_railway": len(proyectos) if railway_ok else 0
        })

    except Exception as e:
        return JSONResponse({
            "ok": False,
            "error": str(e),
            "railway_conectado": False
        })

WEBHOOK_VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "neurox_webhook_2024")

@app.get("/webhook")
async def webhook_verify(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode == "subscribe" and token == WEBHOOK_VERIFY_TOKEN:
        return PlainTextResponse(challenge)
    return PlainTextResponse("Forbidden", status_code=403)

@app.post("/webhook")
async def webhook_router(request: Request):
    """Recibe webhooks de Meta y los reenvía al bot correcto según page_id"""
    try:
        body = await request.body()
        data = json.loads(body)

        if data.get("object") != "instagram":
            return PlainTextResponse("OK")

        for entry in data.get("entry", []):
            messaging = entry.get("messaging", [])
            if not messaging:
                continue

            page_id = messaging[0].get("recipient", {}).get("id")
            if not page_id:
                continue

            webhook_url = obtener_ruta_webhook(page_id)
            if not webhook_url:
                print(f"⚠️ Sin ruta para page_id {page_id}")
                continue

            print(f"📨 Reenviando webhook de {page_id} → {webhook_url}")
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {k: v for k, v in request.headers.items()
                           if k.lower() not in ("host", "content-length")}
                await client.post(webhook_url, content=body, headers=headers)

    except Exception as e:
        print(f"❌ Error en webhook router: {e}")

    return PlainTextResponse("OK")

@app.get("/api/webhook-routes")
async def listar_rutas_webhook():
    rutas = obtener_todas_rutas_webhook()
    return JSONResponse({"ok": True, "rutas": rutas})

@app.post("/api/webhook-routes")
async def crear_ruta_webhook(request: Request):
    data = await request.json()
    page_id = data.get("page_id")
    webhook_url = data.get("webhook_url")
    bot_id = data.get("bot_id")
    if not page_id or not webhook_url:
        return JSONResponse({"ok": False, "error": "page_id y webhook_url requeridos"}, status_code=400)
    registrar_ruta_webhook(page_id, webhook_url, bot_id)
    return JSONResponse({"ok": True, "mensaje": f"Ruta {page_id} → {webhook_url} registrada"})

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3000))
    print(f"\n🚀 Neurox Bot Provisioner iniciando en puerto {port}...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
