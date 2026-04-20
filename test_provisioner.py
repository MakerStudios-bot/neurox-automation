#!/usr/bin/env python3
"""
Script de testing para Neurox Bot Provisioner
Valida toda la cadena de provisioning sin modificar datos reales
"""
import asyncio
import json
import sys
from pathlib import Path

# Agregar backend al path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from provisioner import provisionar_bot
from database import (
    inicializar_db, guardar_bot, obtener_bot,
    obtener_todos_bots, actualizar_bot
)

CONFIG_PATH = Path(__file__).parent / "config"
with open(CONFIG_PATH / "productos.json") as f:
    PRODUCTOS_CONFIG = json.load(f)


def print_test(titulo, resultado=None):
    """Print con formato de test"""
    emoji = "✅" if resultado else "🔍"
    print(f"\n{emoji} {titulo}")
    if resultado:
        print(f"   Resultado: {resultado}")


async def test_db_connection():
    """Test 1: Conectar a la base de datos"""
    print_test("TEST 1: Conexión a Base de Datos")
    try:
        inicializar_db()
        bots = obtener_todos_bots(limite=1)
        print_test("Base de datos iniciada", f"Bots en BD: {len(bots)}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def test_bot_sin_ia():
    """Test 2: Provisionar Bot Automático Sin IA"""
    print_test("TEST 2: Provisionar Bot Automático Sin IA")

    datos_cliente = {
        "nombre_negocio": "Test Negocio SinIA",
        "rubro": "Consultoría",
        "instagram": "test_sinIA_123",
        "contacto_derivacion": "+54 9 1234 5678"
    }

    try:
        resultado = await provisionar_bot(datos_cliente, "bot_automatico_sin_ia")

        if resultado["exito"]:
            print_test("Bot Sin IA provisionado", f"Bot ID: {resultado['bot_id']}")
            return True, resultado["bot_id"]
        else:
            print(f"   ❌ Errores: {resultado['errores']}")
            return False, None

    except Exception as e:
        print(f"   ❌ Excepción: {e}")
        return False, None


async def test_bot_con_ia():
    """Test 3: Provisionar Bot Automático Con IA"""
    print_test("TEST 3: Provisionar Bot Automático Con IA")

    datos_cliente = {
        "nombre_negocio": "Test Negocio ConIA",
        "rubro": "E-commerce",
        "instagram": "test_conIA_456",
        "tono_respuesta": "amigable y profesional",
        "contacto_derivacion": "+54 9 9876 5432",
        "servicios": "Camisetas, pantalones, zapatos",
        "horario_atencion": "Lun-Vie 9:00-18:00"
    }

    try:
        resultado = await provisionar_bot(datos_cliente, "bot_automatico_con_ia")

        if resultado["exito"]:
            print_test("Bot Con IA provisionado", f"Bot ID: {resultado['bot_id']}")
            return True, resultado["bot_id"]
        else:
            print(f"   ❌ Errores: {resultado['errores']}")
            return False, None

    except Exception as e:
        print(f"   ❌ Excepción: {e}")
        return False, None


async def test_vendedor_ia_starter():
    """Test 4: Provisionar Vendedor IA Starter"""
    print_test("TEST 4: Provisionar Vendedor IA Starter")

    datos_cliente = {
        "nombre_negocio": "Test Vendedor Starter",
        "rubro": "Servicios Digitales",
        "instagram": "test_starter_789",
        "tono_venta": "consultivo y cercano",
        "servicios": "Marketing digital, Community management, Diseño",
        "link_agendamiento": "https://calendly.com/test-starter",
        "contacto_whatsapp": "+54 9 1111 2222"
    }

    try:
        resultado = await provisionar_bot(datos_cliente, "vendedor_ia_starter")

        if resultado["exito"]:
            print_test("Vendedor IA Starter provisionado", f"Bot ID: {resultado['bot_id']}")
            return True, resultado["bot_id"]
        else:
            print(f"   ❌ Errores: {resultado['errores']}")
            return False, None

    except Exception as e:
        print(f"   ❌ Excepción: {e}")
        return False, None


async def test_vendedor_ia_pro():
    """Test 5: Provisionar Vendedor IA Pro"""
    print_test("TEST 5: Provisionar Vendedor IA Pro")

    datos_cliente = {
        "nombre_negocio": "Test Vendedor Pro",
        "rubro": "Consultoría Empresarial",
        "instagram": "test_pro_321",
        "tono_venta": "profesional y seguro",
        "servicios": "Auditoría, Asesoría fiscal, Consultoría estratégica",
        "link_agendamiento": "https://calendly.com/test-pro",
        "whatsapp_derivacion": "+54 9 3333 4444"
    }

    try:
        resultado = await provisionar_bot(datos_cliente, "vendedor_ia_pro")

        if resultado["exito"]:
            print_test("Vendedor IA Pro provisionado", f"Bot ID: {resultado['bot_id']}")
            return True, resultado["bot_id"]
        else:
            print(f"   ❌ Errores: {resultado['errores']}")
            return False, None

    except Exception as e:
        print(f"   ❌ Excepción: {e}")
        return False, None


async def test_vendedor_ia_elite():
    """Test 6: Provisionar Vendedor IA Elite"""
    print_test("TEST 6: Provisionar Vendedor IA Elite")

    datos_cliente = {
        "nombre_negocio": "Test Vendedor Elite",
        "rubro": "Agencia Digital",
        "instagram": "test_elite_654",
        "tono_venta": "premium y personalizado",
        "servicios": "Desarrollo web, App mobile, Transformación digital",
        "base_clientes_inactivos": "Sin interacción hace 60 días",
        "whatsapp_derivacion": "+54 9 5555 6666"
    }

    try:
        resultado = await provisionar_bot(datos_cliente, "vendedor_ia_elite")

        if resultado["exito"]:
            print_test("Vendedor IA Elite provisionado", f"Bot ID: {resultado['bot_id']}")
            return True, resultado["bot_id"]
        else:
            print(f"   ❌ Errores: {resultado['errores']}")
            return False, None

    except Exception as e:
        print(f"   ❌ Excepción: {e}")
        return False, None


async def test_obtener_estado(bot_id):
    """Test 7: Obtener estado de bot"""
    print_test(f"TEST 7: Obtener Estado del Bot ID {bot_id}")

    try:
        bot = obtener_bot(bot_id)
        if bot:
            print_test("Bot obtenido", f"Cliente: {bot['cliente_nombre']}, Estado: {bot['estado']}")
            return True
        else:
            print(f"   ❌ Bot no encontrado")
            return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def test_listar_bots():
    """Test 8: Listar todos los bots"""
    print_test("TEST 8: Listar Todos los Bots")

    try:
        bots = obtener_todos_bots(limite=10)
        print_test("Bots listados", f"Total: {len(bots)}")

        if bots:
            print("\n   Bots más recientes:")
            for bot in bots[:5]:
                print(f"   - {bot['cliente_nombre']} ({bot['tipo_servicio']}): {bot['estado']}")

        return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


async def main():
    """Ejecutar todos los tests"""
    print("\n" + "=" * 60)
    print("   🚀 NEUROX BOT PROVISIONER - TEST SUITE")
    print("=" * 60)

    resultados = {
        "BD": await test_db_connection(),
        "Bot Sin IA": None,
        "Bot Con IA": None,
        "Vendedor Starter": None,
        "Vendedor Pro": None,
        "Vendedor Elite": None,
        "Obtener Estado": None,
        "Listar Bots": await test_listar_bots(),
    }

    # Tests de provisioning
    exito, bot_id = await test_bot_sin_ia()
    resultados["Bot Sin IA"] = exito

    exito, bot_id = await test_bot_con_ia()
    resultados["Bot Con IA"] = exito

    exito, bot_id = await test_vendedor_ia_starter()
    resultados["Vendedor Starter"] = exito

    exito, bot_id = await test_vendedor_ia_pro()
    resultados["Vendedor Pro"] = exito

    exito, bot_id = await test_vendedor_ia_elite()
    resultados["Vendedor Elite"] = exito

    # Obtener estado de un bot
    if bot_id:
        resultados["Obtener Estado"] = await test_obtener_estado(bot_id)

    # Resumen
    print("\n" + "=" * 60)
    print("   📊 RESUMEN DE TESTS")
    print("=" * 60)

    passed = sum(1 for v in resultados.values() if v)
    total = len(resultados)

    for test, resultado in resultados.items():
        emoji = "✅" if resultado else "❌"
        print(f"{emoji} {test}")

    print(f"\nTotal: {passed}/{total} tests pasaron")
    print("=" * 60 + "\n")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
