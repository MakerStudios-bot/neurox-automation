#!/usr/bin/env python3
"""
Script para validar la configuración del Neurox Bot Provisioner
Verifica archivos de config, imports, y estructura general
"""
import json
import sys
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config"
BACKEND_PATH = Path(__file__).parent / "backend"

print("\n" + "=" * 60)
print("   🔍 NEUROX BOT PROVISIONER - CONFIG VALIDATOR")
print("=" * 60)

# Test 1: Archivos de configuración
print("\n✓ TEST 1: Validando archivos de configuración")

files_to_check = {
    "productos.json": CONFIG_PATH / "productos.json",
    "prompts.json": CONFIG_PATH / "prompts.json",
    ".env": Path(__file__).parent / ".env"
}

all_exist = True
for name, path in files_to_check.items():
    if path.exists():
        print(f"   ✅ {name} encontrado")
    else:
        print(f"   ❌ {name} NO encontrado")
        all_exist = False

# Test 2: Validar JSON de productos
print("\n✓ TEST 2: Validando config/productos.json")

try:
    with open(CONFIG_PATH / "productos.json") as f:
        productos = json.load(f)

    print(f"   ✅ JSON válido")
    print(f"   ✅ Productos encontrados: {len(productos)}")

    for key, prod in productos.items():
        campos = prod.get("campos_obligatorios", [])
        print(f"      • {key}: {prod.get('nombre')} ({len(campos)} campos)")

except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Validar JSON de prompts
print("\n✓ TEST 3: Validando config/prompts.json")

try:
    with open(CONFIG_PATH / "prompts.json") as f:
        prompts = json.load(f)

    print(f"   ✅ JSON válido")
    print(f"   ✅ Prompts encontrados: {len(prompts)}")

    for key, prompt in prompts.items():
        print(f"      • {key}: {prompt.get('descripcion', 'Sin descripción')}")

except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Validar imports de Python
print("\n✓ TEST 4: Validando imports de Python")

try:
    sys.path.insert(0, str(BACKEND_PATH))

    print("   Validando database.py...")
    from database import inicializar_db, guardar_bot, obtener_todos_bots
    print("      ✅ database.py OK")

    print("   Validando railway_api.py...")
    from railway_api import railway
    print("      ✅ railway_api.py OK")

    print("   Validando meta_api.py...")
    from meta_api import meta
    print("      ✅ meta_api.py OK")

    print("   Validando provisioner.py...")
    from provisioner import provisionar_bot
    print("      ✅ provisioner.py OK")

    print("\n   ✅ Todos los imports son válidos")

except ImportError as e:
    print(f"   ❌ Error de import: {e}")

# Test 5: Validar estructura de archivos
print("\n✓ TEST 5: Validando estructura de directorios")

required_dirs = {
    "backend": BACKEND_PATH,
    "frontend": Path(__file__).parent / "frontend",
    "config": CONFIG_PATH
}

for name, path in required_dirs.items():
    if path.exists() and path.is_dir():
        files = list(path.glob("*"))
        print(f"   ✅ {name}/ ({len(files)} archivos)")
    else:
        print(f"   ❌ {name}/ NO ENCONTRADO")

# Test 6: Validar archivo frontend
print("\n✓ TEST 6: Validando frontend/index.html")

frontend_file = Path(__file__).parent / "frontend" / "index.html"
if frontend_file.exists():
    with open(frontend_file) as f:
        content = f.read()
        if "switchTab" in content and "provisionar" in content:
            print(f"   ✅ Frontend HTML contiene funciones principales")
        else:
            print(f"   ⚠️ Frontend HTML podría estar incompleto")
else:
    print(f"   ❌ frontend/index.html NO ENCONTRADO")

# Test 7: Validar .env
print("\n✓ TEST 7: Validando variables de entorno")

env_file = Path(__file__).parent / ".env"
required_vars = ["RAILWAY_API_TOKEN"]

if env_file.exists():
    with open(env_file) as f:
        env_content = f.read()
        for var in required_vars:
            if var in env_content:
                print(f"   ✅ {var} está configurado")
            else:
                print(f"   ⚠️ {var} NO está configurado (pero puede no ser necesario para testing)")
else:
    print(f"   ⚠️ .env NO ENCONTRADO (usar variables de entorno del sistema)")

# Resumen
print("\n" + "=" * 60)
print("   📊 VALIDACIÓN COMPLETADA")
print("=" * 60)
print("\nPróximos pasos:")
print("1. Ejecutar: python test_provisioner.py (test de funcionalidad)")
print("2. Ejecutar: uvicorn backend.main:app --reload (iniciar servidor)")
print("3. Visitar: http://localhost:8000 (abrir dashboard)")
print("\n")
