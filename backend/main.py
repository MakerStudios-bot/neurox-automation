"""
Neurox Bot Provisioner - Automatiza instalación completa de bots para clientes
"""
import os
import asyncio
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from dotenv import load_dotenv

from provisioner import provisionar_bot, obtener_estado_provisioning
from database import obtener_todos_bots
from railway_api import railway

load_dotenv()

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
    """Retorna lista de servicios disponibles"""
    return JSONResponse({
        "ok": True,
        "servicios": SERVICIOS
    })

@app.post("/api/provisionar")
async def provisionar_nuevo_bot(request: Request, background_tasks: BackgroundTasks):
    """
    Inicia el provisioning de un nuevo bot.
    Corre en background y configura todo automáticamente.
    """
    try:
        data = await request.json()

        cliente_nombre = data.get("cliente_nombre", "").strip()
        cliente_instagram = data.get("cliente_instagram", "").strip()
        cliente_clave = data.get("cliente_clave", "").strip()
        tipo_servicio = data.get("tipo_servicio", "").strip()

        # Validación
        if not all([cliente_nombre, cliente_instagram, cliente_clave, tipo_servicio]):
            return JSONResponse(
                {"ok": False, "error": "Faltan datos requeridos"},
                status_code=400
            )

        if tipo_servicio not in SERVICIOS:
            return JSONResponse(
                {"ok": False, "error": "Tipo de servicio no válido"},
                status_code=400
            )

        servicio = SERVICIOS[tipo_servicio]

        # Dispara provisioning en background
        background_tasks.add_task(
            provisionar_bot,
            cliente_nombre,
            cliente_instagram,
            cliente_clave,
            tipo_servicio
        )

        return JSONResponse({
            "ok": True,
            "mensaje": f"Provisionando {servicio['nombre']}...",
            "cliente": cliente_nombre,
            "instagram": cliente_instagram,
            "servicio": servicio['nombre']
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3000))
    print(f"\n🚀 Neurox Bot Provisioner iniciando en puerto {port}...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
