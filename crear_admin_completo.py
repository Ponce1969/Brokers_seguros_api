#!/usr/bin/env python3
"""
Script para inicializar la base de datos y crear el administrador del sistema.

Este script realiza las siguientes acciones:
1. Elimina los contenedores y volúmenes de Docker para empezar desde cero
2. Levanta los servicios nuevamente
3. Inicializa la base de datos con el usuario administrador
4. Verifica que el corredor administrador se haya creado correctamente

Datos del administrador:
- Número: 4554
- Nombre: Rodrigo Ponce
- Email: rpd.ramas@gmail.com
- Documento: 17775367
- Comisión: 10%
- Usuario: rponce
- Contraseña: Gallinal2218**
"""

import requests
import json
import time
import subprocess
import os

# URL base de la API
BASE_URL = "http://localhost:8000"

# Directorio del proyecto
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Datos del administrador para verificación
ADMIN_DATA = {
    "numero": 4554,
    "nombres": "Rodrigo",
    "apellidos": "Ponce",
    "documento": "17775367",
    "email": "rpd.ramas@gmail.com",
    "username": "rponce",
    "password": "Gallinal2218**",
    "comision": 10.0
}

def eliminar_contenedores_y_volumenes():
    """Elimina los contenedores y volúmenes de Docker"""
    try:
        print("\n🔄 Eliminando contenedores y volúmenes de Docker...")
        result = subprocess.run(
            ["docker-compose", "down", "-v"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("\n✅ Contenedores y volúmenes eliminados exitosamente")
            print(result.stdout)
            return True
        else:
            print(f"\n❌ Error al eliminar contenedores y volúmenes: {result.returncode}")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

def levantar_servicios():
    """Levanta los servicios de Docker"""
    try:
        print("\n🔄 Levantando servicios de Docker...")
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("\n✅ Servicios levantados exitosamente")
            print(result.stdout)
            return True
        else:
            print(f"\n❌ Error al levantar servicios: {result.returncode}")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

def verificar_corredor():
    """Verifica si el corredor fue creado correctamente"""
    try:
        # Esperar a que la API esté disponible
        print("\n🔄 Esperando a que la API esté disponible...")
        time.sleep(5)  # Dar tiempo a que el servicio esté completamente iniciado
        
        # Endpoint para obtener el corredor por número
        url = f"{BASE_URL}/api/v1/corredores/numero/{ADMIN_DATA['numero']}"
        
        # Realizar la solicitud GET
        response = requests.get(url)
        
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            print("\n✅ Corredor administrador encontrado correctamente")
            admin_info = response.json()
            print(f"ID: {admin_info.get('id')} (autoincremental)")
            print(f"Numero: {admin_info.get('numero')} (identificador de negocio)")
            print(f"Nombre: {admin_info.get('nombre')}")
            print(f"Email: {admin_info.get('email')}")
            print(f"Documento: {admin_info.get('documento')}")
            print(f"Tipo: {admin_info.get('tipo')}")
            return True
        else:
            print(f"\n❌ Error al verificar corredor: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

def inicializar_db():
    """Inicializa la base de datos ejecutando el script init_db.py"""
    try:
        print("\n🔄 Inicializando base de datos...")
        # Ejecutar el script init_db.py dentro del contenedor
        result = subprocess.run(
            ["docker", "exec", "fastapi_backend", "python", "-m", "app.db.init_db"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("\n✅ Base de datos inicializada exitosamente")
            return True
        else:
            print(f"\n❌ Error al inicializar base de datos: {result.returncode}")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n🔄 Iniciando proceso de configuración del sistema...")
    
    # Paso 1: Eliminar contenedores y volúmenes existentes
    if eliminar_contenedores_y_volumenes():
        # Paso 2: Levantar servicios nuevamente
        if levantar_servicios():
            # Paso 3: Inicializar la base de datos con el usuario administrador
            if inicializar_db():
                # Paso 4: Verificar que el corredor administrador se haya creado correctamente
                print("\n🔄 Verificando corredor administrador...")
                verificar_corredor()
                
                print("\n✅ Proceso completado exitosamente")
                print(f"\nCredenciales del administrador:\n  Usuario: {ADMIN_DATA['username']}\n  Contraseña: {ADMIN_DATA['password']}")
            else:
                print("\n❌ Error al inicializar la base de datos")
        else:
            print("\n❌ Error al levantar los servicios")
    else:
        print("\n❌ Error al eliminar contenedores y volúmenes")

