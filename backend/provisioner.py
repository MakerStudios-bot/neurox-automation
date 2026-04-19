"""
Orquestador principal de provisioning
Coordina Railway, Meta, y base de datos
"""
import asyncio
import json
from typing import Optional, Dict, Any
from datetime import datetime

from railway_api import railway
from meta_api import meta
from database import (
    guardar_bot, actualizar_bot, obtener_bot,
    registrar_log, obtener_todos_bots
)

# Mapeo de templates en Railway
RAILWAY_TEMPLATES = {
    "bot_automatico_sin_ia": "mellow-elegance",  # mellow-elegance: 49a1dc7a-c29d-4631-baff-5fb29e17d6e4
    "bot_automatico_con_ia": "mellow-elegance",  # Mismo template, diferentes instrucciones
    "vendedor_ia_starter": "radiant-ambition",   # radiant-ambition: eaa5e41c-06a2-497b-8696-1417a9f62485
    "vendedor_ia_pro": "radiant-ambition",       # Mismo template, diferentes instrucciones
    "vendedor_ia_elite": "radiant-ambition",     # Mismo template, diferentes instrucciones
}

VARIABLES_COMPARTIDAS = {
    "TOKEN_DE_VERIFICACIÓN": "neurox_verification_token_123",
    "APP_SECRET": "neurox_app_secret_456",
    "CLAVE_API_ANTROPICA": "sk-ant-...tu-clave-aqui",
}

async def provisionar_bot(
    cliente_nombre: str,
    cliente_instagram: str,
    cliente_clave: str,
    tipo_servicio: str
) -> Dict[str, Any]:
    """
    Provisiona un bot completo para un cliente.
    Orquesta todas las integraciones.
    """
    print(f"\n📦 Iniciando provisioning: {cliente_nombre} (@{cliente_instagram})")

    resultado = {
        "exito": False,
        "bot_id": None,
        "mensaje": "",
        "errores": []
    }

    # Paso 1: Guardar en BD
    try:
        bot_id = guardar_bot(cliente_nombre, cliente_instagram, tipo_servicio)
        if bot_id == -1:
            resultado["errores"].append("Cliente ya existe")
            return resultado

        resultado["bot_id"] = bot_id
        registrar_log(bot_id, "iniciado", "Provisioning iniciado")
        print(f"✓ Bot guardado en BD (ID: {bot_id})")

    except Exception as e:
        resultado["errores"].append(f"Error guardando en BD: {str(e)}")
        return resultado

    # Paso 2: Validar credenciales Instagram
    try:
        print(f"🔐 Validando credenciales de @{cliente_instagram}...")
        validacion = await meta.validar_credenciales_instagram(
            cliente_instagram,
            cliente_clave
        )

        if not validacion.get("valido"):
            resultado["errores"].append("Credenciales de Instagram inválidas")
            actualizar_bot(bot_id, estado="error_credenciales")
            registrar_log(bot_id, "error", "Credenciales inválidas")
            return resultado

        instagram_id = validacion.get("instagram_id")
        print(f"✓ Credenciales validadas")

    except Exception as e:
        resultado["errores"].append(f"Error validando Instagram: {str(e)}")
        actualizar_bot(bot_id, estado="error_instagram")
        registrar_log(bot_id, "error", str(e))
        return resultado

    # Paso 3: Clonar proyecto en Railway
    try:
        template_id = RAILWAY_TEMPLATES.get(tipo_servicio)
        if not template_id:
            resultado["errores"].append(f"Template no encontrado: {tipo_servicio}")
            actualizar_bot(bot_id, estado="error_template")
            return resultado

        print(f"🚂 Clonando proyecto en Railway...")
        nuevo_proyecto_nombre = f"neurox-{cliente_instagram}-{tipo_servicio[:4]}"

        proyecto_clonado_id = await railway.clonar_proyecto(
            template_id,
            nuevo_proyecto_nombre
        )

        if not proyecto_clonado_id:
            resultado["errores"].append("Error clonando proyecto en Railway")
            actualizar_bot(bot_id, estado="error_railway")
            registrar_log(bot_id, "error", "Fallo al clonar en Railway")
            return resultado

        actualizar_bot(bot_id, railway_project_id=proyecto_clonado_id)
        print(f"✓ Proyecto clonado: {proyecto_clonado_id}")

    except Exception as e:
        resultado["errores"].append(f"Error en Railway: {str(e)}")
        actualizar_bot(bot_id, estado="error_railway")
        registrar_log(bot_id, "error", str(e))
        return resultado

    # Paso 4: Configurar variables de entorno
    try:
        print(f"⚙️ Configurando variables de entorno...")

        # Variables compartidas
        for var_name, var_value in VARIABLES_COMPARTIDAS.items():
            await railway.configurar_variable(
                proyecto_clonado_id,
                var_name,
                var_value
            )
            print(f"  ✓ {var_name}")

        # Variables del cliente
        variables_cliente = {
            "INSTAGRAM_USERNAME": cliente_instagram,
            "INSTAGRAM_PASSWORD": cliente_clave,
            "CLIENTE_NOMBRE": cliente_nombre,
            "INSTAGRAM_ID": instagram_id,
        }

        for var_name, var_value in variables_cliente.items():
            await railway.configurar_variable(
                proyecto_clonado_id,
                var_name,
                var_value
            )
            print(f"  ✓ {var_name}")

        registrar_log(bot_id, "variables_configuradas", "Variables de entorno configuradas")

    except Exception as e:
        resultado["errores"].append(f"Error configurando variables: {str(e)}")
        actualizar_bot(bot_id, estado="error_variables")
        registrar_log(bot_id, "error", str(e))
        return resultado

    # Paso 5: Conectar webhook a Instagram
    try:
        print(f"🔗 Conectando webhook a Instagram...")

        token_acceso = await meta.obtener_token_acceso(cliente_instagram)

        webhook_conectado = await meta.conectar_webhook(
            instagram_id,
            f"https://neurox-{cliente_instagram}.railway.app/webhook",
            token_acceso
        )

        if webhook_conectado:
            actualizar_bot(bot_id, token_acceso=token_acceso)
            print(f"✓ Webhook conectado")
        else:
            print(f"⚠️ Webhook no conectado (continuando)")

        registrar_log(bot_id, "webhook_conectado", "Webhook de Instagram configurado")

    except Exception as e:
        # No falla el provisioning si webhook falla
        print(f"⚠️ Error en webhook: {e}")
        registrar_log(bot_id, "warning", f"Webhook: {e}")

    # Paso 6: Desplegar
    try:
        print(f"🚀 Desplegando...")
        await railway.desplegar_servicio(proyecto_clonado_id)
        print(f"✓ Desplegado")

        registrar_log(bot_id, "desplegado", "Servicio desplegado en Railway")

    except Exception as e:
        resultado["errores"].append(f"Error desplegando: {str(e)}")
        actualizar_bot(bot_id, estado="error_deploy")
        registrar_log(bot_id, "error", str(e))
        return resultado

    # Paso 7: Finalizar
    try:
        actualizar_bot(
            bot_id,
            estado="listo",
            fecha_listo=datetime.now().isoformat(),
            instagram_id=instagram_id,
            metadata={
                "proyecto_railway": proyecto_clonado_id,
                "tipo_servicio": tipo_servicio,
                "fecha_provisioning": datetime.now().isoformat()
            }
        )

        registrar_log(bot_id, "completado", "Provisioning completado con éxito")

        resultado["exito"] = True
        resultado["mensaje"] = f"✅ Bot provisioned para {cliente_nombre}"
        print(f"\n✅ ¡Provisioning completado para {cliente_nombre}!\n")

    except Exception as e:
        resultado["errores"].append(f"Error finalizando: {str(e)}")

    return resultado

async def obtener_estado_provisioning(bot_id: int) -> Dict[str, Any]:
    """Obtiene el estado actual de un bot"""
    bot = obtener_bot(bot_id)

    if not bot:
        return {"error": "Bot no encontrado"}

    return {
        "bot_id": bot["id"],
        "cliente": bot["cliente_nombre"],
        "instagram": bot["cliente_instagram"],
        "servicio": bot["tipo_servicio"],
        "estado": bot["estado"],
        "fecha_creacion": bot["fecha_creacion"],
        "fecha_listo": bot["fecha_listo"],
        "railway_project": bot["railway_project_id"],
    }
