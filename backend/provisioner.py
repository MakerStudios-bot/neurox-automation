"""
Orquestador principal de provisioning
Coordina Railway, Meta, y base de datos
Configura bots basado en producto y membresía
"""
import asyncio
import json
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from railway_api import railway
from database import (
    guardar_bot, actualizar_bot, obtener_bot,
    registrar_log, obtener_todos_bots, registrar_ruta_webhook
)

CONFIG_PATH = Path(__file__).parent.parent / "config"
with open(CONFIG_PATH / "productos.json") as f:
    PRODUCTOS_CONFIG = json.load(f)
with open(CONFIG_PATH / "prompts.json") as f:
    PROMPTS_CONFIG = json.load(f)


async def provisionar_bot(
    datos_cliente: Dict[str, Any],
    tipo_servicio: str
) -> Dict[str, Any]:
    cliente_nombre = datos_cliente.get("nombre_negocio") or datos_cliente.get("cliente_nombre")
    cliente_instagram = datos_cliente.get("instagram", "").strip().replace("@", "")
    access_token_meta = datos_cliente.get("access_token_meta", "").strip()
    ig_business_id = datos_cliente.get("instagram_business_account_id", "").strip()
    descripcion_negocio = datos_cliente.get("descripcion_negocio", "").strip()
    productos_precios = datos_cliente.get("productos_precios", "").strip()
    servicios = datos_cliente.get("servicios", "").strip()
    tono = datos_cliente.get("tono_venta", "").strip() or datos_cliente.get("tono_respuesta", "amigable").strip()
    link_agendamiento = datos_cliente.get("link_agendamiento", "").strip()
    whatsapp = datos_cliente.get("whatsapp_derivacion", "").strip() or datos_cliente.get("contacto_whatsapp", "").strip() or datos_cliente.get("contacto_derivacion", "").strip()

    print(f"\n📦 Iniciando provisioning: {cliente_nombre} (@{cliente_instagram})")
    print(f"   Producto: {tipo_servicio}")

    resultado = {"exito": False, "bot_id": None, "mensaje": "", "errores": []}
    config_producto = PRODUCTOS_CONFIG.get(tipo_servicio, {})

    # Paso 1: Guardar en BD
    try:
        bot_id = guardar_bot(cliente_nombre, cliente_instagram, tipo_servicio, metadata=datos_cliente)
        if bot_id == -1:
            resultado["errores"].append("Cliente ya existe")
            return resultado
        resultado["bot_id"] = bot_id
        registrar_log(bot_id, "iniciado", f"Provisioning de {config_producto.get('nombre')}")
        print(f"✓ Bot guardado en BD (ID: {bot_id})")
    except Exception as e:
        resultado["errores"].append(f"Error guardando en BD: {str(e)}")
        return resultado

    # Paso 2: Clonar proyecto en Railway
    proyecto_clonado_id = None
    try:
        template_nombre = config_producto.get("template", "radiant-ambition")
        nuevo_proyecto_nombre = f"neurox-{cliente_instagram}"

        print(f"🚂 Clonando proyecto en Railway ({template_nombre})...")
        proyecto_clonado_id = await railway.clonar_proyecto(template_nombre, nuevo_proyecto_nombre)

        if not proyecto_clonado_id:
            resultado["errores"].append("Error clonando proyecto en Railway")
            actualizar_bot(bot_id, estado="error_railway")
            registrar_log(bot_id, "error", "Fallo al clonar en Railway")
            return resultado

        actualizar_bot(bot_id, railway_project_id=proyecto_clonado_id)
        registrar_log(bot_id, "railway_clonado", f"Proyecto: {proyecto_clonado_id}")
        print(f"✓ Proyecto clonado: {proyecto_clonado_id}")

    except Exception as e:
        resultado["errores"].append(f"Error en Railway: {str(e)}")
        actualizar_bot(bot_id, estado="error_railway")
        registrar_log(bot_id, "error", str(e))
        return resultado

    # Paso 3: Configurar variables del bot
    try:
        print(f"⚙️ Configurando variables del bot...")

        env_id = getattr(railway, '_last_env_id', None)
        service_id = getattr(railway, '_last_service_id', None)

        system_prompt = f"Eres vendedor de {cliente_nombre}."
        if descripcion_negocio:
            system_prompt = f"Eres vendedor de {cliente_nombre}. {descripcion_negocio}."
        system_prompt += f" Responde SIEMPRE en español, máximo 3 oraciones, sin listas con viñetas. Sé {tono}."

        productos_texto = productos_precios or servicios or ""

        variables_bot = {
            "ACCESS_TOKEN": access_token_meta,
            "INSTAGRAM_BUSINESS_ACCOUNT_ID": ig_business_id,
            "BUSINESS_NAME": cliente_nombre,
            "SYSTEM_PROMPT": system_prompt,
            "CLIENTE_NOMBRE": cliente_nombre,
            "TIPO_SERVICIO": tipo_servicio,
            "VERIFY_TOKEN": "neurox_webhook_2024",
        }

        if productos_texto:
            variables_bot["PRODUCTOS_PROMPT"] = productos_texto
            variables_bot["PRODUCTOS_DETALLE"] = productos_texto

        if link_agendamiento:
            variables_bot["CAL_LINK"] = link_agendamiento

        if whatsapp:
            variables_bot["WHATSAPP_DERIVACION"] = whatsapp

        # Usar variableCollectionUpsert para setear todo de una vez
        if env_id and service_id:
            from railway_api import RAILWAY_API_URL, RAILWAY_ACCESS_TOKEN
            import httpx

            query = """
            mutation SetVars($input: VariableCollectionUpsertInput!) {
                variableCollectionUpsert(input: $input)
            }
            """
            payload = {
                "query": query,
                "variables": {
                    "input": {
                        "projectId": proyecto_clonado_id,
                        "environmentId": env_id,
                        "serviceId": service_id,
                        "variables": variables_bot
                    }
                }
            }

            headers = {
                "Authorization": f"Bearer {RAILWAY_ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(RAILWAY_API_URL, json=payload, headers=headers)
                data = response.json()
                if data.get("data", {}).get("variableCollectionUpsert"):
                    print(f"  ✓ Variables configuradas ({len(variables_bot)} variables)")
                else:
                    print(f"  ⚠️ Error seteando variables: {data}")

        registrar_log(bot_id, "variables_configuradas", f"{len(variables_bot)} variables configuradas")

    except Exception as e:
        print(f"⚠️ Error configurando variables: {e}")
        registrar_log(bot_id, "warning", f"Variables: {str(e)}")

    # Paso 4: Obtener URL del bot y registrar ruta de webhook
    try:
        url_bot = await railway.obtener_url_servicio(proyecto_clonado_id)
        if url_bot:
            webhook_url = f"https://{url_bot}/webhook"
            actualizar_bot(bot_id, url_bot=f"https://{url_bot}")
            print(f"✓ URL del bot: https://{url_bot}")

            # Registrar ruta de webhook
            if ig_business_id:
                registrar_ruta_webhook(ig_business_id, webhook_url, bot_id)
                print(f"✓ Ruta webhook registrada: {ig_business_id} → {webhook_url}")
                registrar_log(bot_id, "webhook_registrado", f"{ig_business_id} → {webhook_url}")
        else:
            print(f"⚠️ No se pudo obtener URL del bot")

    except Exception as e:
        print(f"⚠️ Error obteniendo URL: {e}")
        registrar_log(bot_id, "warning", f"URL: {str(e)}")

    # Paso 5: Finalizar
    try:
        actualizar_bot(
            bot_id,
            estado="listo",
            fecha_listo=datetime.now().isoformat(),
            instagram_id=ig_business_id,
            token_acceso=access_token_meta[:20] + "..." if access_token_meta else "",
            railway_service_id=service_id,
            metadata={
                "proyecto_railway": proyecto_clonado_id,
                "service_id": service_id,
                "environment_id": env_id,
                "tipo_servicio": tipo_servicio,
                "business_name": cliente_nombre,
                "fecha_provisioning": datetime.now().isoformat()
            }
        )

        registrar_log(bot_id, "completado", "Provisioning completado")

        resultado["exito"] = True
        resultado["mensaje"] = f"Bot provisionado para {cliente_nombre}"
        print(f"\n✅ ¡Provisioning completado para {cliente_nombre}!\n")

    except Exception as e:
        resultado["errores"].append(f"Error finalizando: {str(e)}")

    return resultado


async def obtener_estado_provisioning(bot_id: int) -> Dict[str, Any]:
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
