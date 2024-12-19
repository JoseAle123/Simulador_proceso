# CPU Procesamiento Simulador

Este proyecto es un simulador visual de planificación de procesos en una CPU, utilizando algoritmos como **FCFS (First Come First Serve)**, **Round Robin (RR)** y **Shortest Job First (SJF)**. Fue desarrollado en Python utilizando PyQt5 para la interfaz gráfica.

## Requisitos Previos

Asegúrate de tener instalados los siguientes elementos antes de ejecutar el proyecto:

1. **Python 3.11+**
2. **Módulos de Python:**
   - PyQt5
   - psutil

## Instalación

Para instalar los módulos requeridos, sigue los pasos a continuación:

1. Crear y activar un entorno virtual:

   - **Windows**:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

   - **Linux/Mac**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

2. Instalar dependencias con el siguiente comando:

   ```bash
   pip install -r requirements.txt
   ```
3. Ejecuta el archivo
   ```bash
   python3 main.py
   ```