"""
Módulo para registrar el historial de textos leídos por síntesis de voz.
Guarda un JSON con información de cada lectura.
"""
import json
import os
from datetime import datetime
from pathlib import Path


LOG_DIR = Path(__file__).resolve().parent.parent / 'logs'
LOG_FILE = LOG_DIR / 'audio_readings.json'


def registrar_lectura(id_publicacion, titulo, texto, id_usuario=None):
    """
    Registra una lectura de texto por síntesis de voz en JSON.
    
    Args:
        id_publicacion (int): ID de la publicación leída
        titulo (str): Título de la publicación
        texto (str): Texto que fue leído
        id_usuario (int, optional): ID del usuario que escuchó (si está logged in)
    
    Returns:
        bool: True si se guardó exitosamente, False en caso contrario
    """
    try:
        # Asegurar que el directorio existe
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        
        # Crear registro
        registro = {
            "id_publicacion": id_publicacion,
            "titulo": titulo,
            "texto": texto,
            "id_usuario": id_usuario,
            "fecha_hora": datetime.now().isoformat(),
            "timestamp": datetime.now().timestamp()
        }
        
        # Leer registros existentes
        registros = []
        if LOG_FILE.exists():
            try:
                with open(LOG_FILE, 'r', encoding='utf-8') as f:
                    registros = json.load(f)
            except json.JSONDecodeError:
                # Si el archivo está corrupto, comenzar de cero
                registros = []
        
        # Añadir nuevo registro
        registros.append(registro)
        
        # Guardar de vuelta
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(registros, f, ensure_ascii=False, indent=2)
        
        return True
    
    except Exception as e:
        print(f"Error al registrar lectura: {e}")
        return False


def obtener_todas_las_lecturas():
    """
    Obtiene todos los registros de lecturas.
    
    Returns:
        list: Lista de registros o lista vacía si no hay registros
    """
    try:
        if LOG_FILE.exists():
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error al leer registros: {e}")
    
    return []


def obtener_lecturas_por_publicacion(id_publicacion):
    """
    Obtiene todos los registros de una publicación específica.
    
    Args:
        id_publicacion (int): ID de la publicación
    
    Returns:
        list: Lista de registros de esa publicación
    """
    todas = obtener_todas_las_lecturas()
    return [r for r in todas if r['id_publicacion'] == id_publicacion]


def obtener_lecturas_por_usuario(id_usuario):
    """
    Obtiene todos los registros de un usuario específico.
    
    Args:
        id_usuario (int): ID del usuario
    
    Returns:
        list: Lista de registros del usuario
    """
    todas = obtener_todas_las_lecturas()
    return [r for r in todas if r['id_usuario'] == id_usuario]
