"""
Neurox Bot Provisioner - Automatiza la instalación de bots para clientes
"""
import os
import json
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from dotenv import load_dotenv
import httpx

load_dotenv()

app = FastAPI(title="Neurox Bot Provisioner", version="1.0.0")

# Configuración
RAILWAY_API_TOKEN = os.getenv("RAILWAY_API_TOKEN", "")
RAILWAY_API_URL = os.getenv("RAILWAY_API_URL", "https://api.railway.app/graphql")
NEUROX_VENDEDOR_NOMBRE = os.getenv("NEUROX_VENDEDOR_NOMBRE", "María")

# Servir archivos estáticos del frontend
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

SERVICIOS = {
    "bot_automatico": {
        "nombre": "Bot Automático Instagram",
        "precio": 180000,
        "template": "neurox-bot-automatico",
    },
    "vendedor_ia_starter": {
        "nombre": "Vendedor IA Starter",
        "precio": 24000,
        "tipo_precio": "mensual",
        "template": "neurox-vendedor-ia-starter",
    },
    "vendedor_ia_pro": {
        "nombre": "Vendedor IA Pro",
        "precio": 55000,
        "tipo_precio": "mensual",
        "template": "neurox-vendedor-ia-pro",
    },
    "vendedor_ia_elite": {
        "nombre": "Vendedor IA Elite",
        "precio": 105000,
        "tipo_precio": "mensual",
        "template": "neurox-vendedor-ia-elite",
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
async def provisionar_bot(request: Request, background_tasks: BackgroundTasks):
    """
    Provisiona un nuevo bot para un cliente

    Requiere:
    - cliente_nombre: nombre del cliente
    - cliente_instagram: usuario de Instagram del cliente
    - cliente_clave: clave/contraseña de Instagram
    - tipo_servicio: bot_automatico, vendedor_ia_starter, etc.
    """
    try:
        data = await request.json()

        cliente_nombre = data.get("cliente_nombre")
        cliente_instagram = data.get("cliente_instagram")
        cliente_clave = data.get("cliente_clave")
        tipo_servicio = data.get("tipo_servicio")

        if not all([cliente_nombre, cliente_instagram, cliente_clave, tipo_servicio]):
            return JSONResponse(
                {"error": "Faltan datos requeridos"},
                status_code=400
            )

        if tipo_servicio not in SERVICIOS:
            return JSONResponse(
                {"error": "Tipo de servicio no válido"},
                status_code=400
            )

        # Validar que Instagram no esté vacío
        if not cliente_instagram.strip():
            return JSONResponse(
                {"error": "Usuario de Instagram no puede estar vacío"},
                status_code=400
            )

        servicio = SERVICIOS[tipo_servicio]
        print(f"\n📦 Provisionando {servicio['nombre']} para {cliente_nombre}")

        # Dispara el provisioning en background
        background_tasks.add_task(
            procesar_provisioning,
            cliente_nombre,
            cliente_instagram,
            cliente_clave,
            tipo_servicio,
            servicio
        )

        return JSONResponse({
            "ok": True,
            "mensaje": f"Provisionando {servicio['nombre']}...",
            "cliente": cliente_nombre,
            "servicio": servicio['nombre']
        })

    except Exception as e:
        print(f"❌ Error en provisioning: {e}")
        return JSONResponse(
            {"error": str(e)},
            status_code=500
        )

async def procesar_provisioning(cliente_nombre, cliente_instagram, cliente_clave, tipo_servicio, servicio):
    """Procesa el provisioning del bot (corre en background)"""
    try:
        print(f"✓ Iniciando provisioning para {cliente_nombre}...")

        # TODO: Aquí irá la lógica de:
        # 1. Clonar template en Railway
        # 2. Configurar credenciales (cliente_instagram, cliente_clave)
        # 3. Conectar a Meta/Instagram
        # 4. Validar que funciona
        # 5. Notificar cuando esté listo

        print(f"✅ Bot listo para {cliente_nombre}")

    except Exception as e:
        print(f"❌ Error procesando provisioning: {e}")

@app.get("/api/status")
async def status():
    """Retorna estado de la aplicación"""
    railway_ok = bool(RAILWAY_API_TOKEN)

    return JSONResponse({
        "ok": True,
        "railway_conectado": railway_ok,
        "vendedor_nombre": NEUROX_VENDEDOR_NOMBRE
    })

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
