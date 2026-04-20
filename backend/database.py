"""
Base de datos SQLite para guardar historial de provisioning
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

DB_PATH = Path(__file__).parent.parent / "neurox_provisioning.db"

def inicializar_db():
    """Crea las tablas si no existen"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabla de bots provisionados
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bots_provisionados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_nombre TEXT NOT NULL,
            cliente_instagram TEXT NOT NULL UNIQUE,
            tipo_servicio TEXT NOT NULL,
            railway_project_id TEXT,
            railway_service_id TEXT,
            instagram_id TEXT,
            token_acceso TEXT,
            estado TEXT DEFAULT 'provisionando',
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_listo TIMESTAMP,
            url_bot TEXT,
            metadata TEXT
        )
    """)

    # Tabla de logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs_provisioning (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bot_id INTEGER,
            evento TEXT NOT NULL,
            mensaje TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bot_id) REFERENCES bots_provisionados(id)
        )
    """)

    # Tabla de rutas de webhook (page_id → URL del bot)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS webhook_routes (
            page_id TEXT PRIMARY KEY,
            webhook_url TEXT NOT NULL,
            bot_id INTEGER,
            activo INTEGER DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bot_id) REFERENCES bots_provisionados(id)
        )
    """)

    conn.commit()
    conn.close()

def registrar_ruta_webhook(page_id: str, webhook_url: str, bot_id: int = None) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO webhook_routes (page_id, webhook_url, bot_id)
            VALUES (?, ?, ?)
        """, (page_id, webhook_url, bot_id))
        conn.commit()
        return True
    finally:
        conn.close()

def obtener_ruta_webhook(page_id: str) -> Optional[str]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT webhook_url FROM webhook_routes WHERE page_id = ? AND activo = 1",
            (page_id,)
        )
        row = cursor.fetchone()
        return row[0] if row else None
    finally:
        conn.close()

def obtener_todas_rutas_webhook() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM webhook_routes ORDER BY fecha_creacion DESC")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def guardar_bot(
    cliente_nombre: str,
    cliente_instagram: str,
    tipo_servicio: str,
    railway_project_id: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> int:
    """Guarda un nuevo bot en la BD"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO bots_provisionados
            (cliente_nombre, cliente_instagram, tipo_servicio, railway_project_id, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (
            cliente_nombre,
            cliente_instagram,
            tipo_servicio,
            railway_project_id,
            json.dumps(metadata or {})
        ))

        bot_id = cursor.lastrowid
        conn.commit()
        return bot_id

    except sqlite3.IntegrityError:
        print(f"⚠️ Bot para @{cliente_instagram} ya existe")
        return -1
    finally:
        conn.close()

def actualizar_bot(
    bot_id: int,
    **kwargs
) -> bool:
    """Actualiza datos de un bot"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    campos_permitidos = [
        'cliente_nombre', 'cliente_instagram', 'tipo_servicio',
        'railway_project_id', 'railway_service_id', 'instagram_id',
        'token_acceso', 'estado', 'fecha_listo', 'url_bot', 'metadata'
    ]

    campos = []
    valores = []

    for key, value in kwargs.items():
        if key in campos_permitidos:
            campos.append(f"{key} = ?")
            if key == 'metadata' and isinstance(value, dict):
                valores.append(json.dumps(value))
            else:
                valores.append(value)

    if not campos:
        return False

    valores.append(bot_id)

    try:
        query = f"UPDATE bots_provisionados SET {', '.join(campos)} WHERE id = ?"
        cursor.execute(query, valores)
        conn.commit()
        return cursor.rowcount > 0

    finally:
        conn.close()

def obtener_bot(bot_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene datos de un bot específico"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM bots_provisionados WHERE id = ?", (bot_id,))
        row = cursor.fetchone()

        if row:
            bot_dict = dict(row)
            if bot_dict.get('metadata'):
                bot_dict['metadata'] = json.loads(bot_dict['metadata'])
            return bot_dict

        return None

    finally:
        conn.close()

def obtener_bot_por_instagram(instagram: str) -> Optional[Dict[str, Any]]:
    """Obtiene un bot por username de Instagram"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT * FROM bots_provisionados WHERE cliente_instagram = ?",
            (instagram,)
        )
        row = cursor.fetchone()

        if row:
            bot_dict = dict(row)
            if bot_dict.get('metadata'):
                bot_dict['metadata'] = json.loads(bot_dict['metadata'])
            return bot_dict

        return None

    finally:
        conn.close()

def obtener_todos_bots(limite: int = 100) -> List[Dict[str, Any]]:
    """Obtiene lista de todos los bots"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT * FROM bots_provisionados
            ORDER BY fecha_creacion DESC
            LIMIT ?
        """, (limite,))

        bots = []
        for row in cursor.fetchall():
            bot_dict = dict(row)
            if bot_dict.get('metadata'):
                bot_dict['metadata'] = json.loads(bot_dict['metadata'])
            bots.append(bot_dict)

        return bots

    finally:
        conn.close()

def registrar_log(bot_id: int, evento: str, mensaje: str = ""):
    """Registra un evento de provisioning"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO logs_provisioning (bot_id, evento, mensaje)
            VALUES (?, ?, ?)
        """, (bot_id, evento, mensaje))

        conn.commit()

    finally:
        conn.close()

def obtener_logs_bot(bot_id: int) -> List[Dict[str, Any]]:
    """Obtiene logs de un bot específico"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT * FROM logs_provisioning
            WHERE bot_id = ?
            ORDER BY fecha DESC
        """, (bot_id,))

        logs = [dict(row) for row in cursor.fetchall()]
        return logs

    finally:
        conn.close()

# Inicializar BD al importar
inicializar_db()
