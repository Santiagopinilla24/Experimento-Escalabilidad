# Experimento de Escalabilidad: Análisis de Consumo por Área en AWS

Este proyecto implementa la arquitectura y los scripts necesarios para llevar a cabo el experimento de escalabilidad (ASR 1), pasando de 5,000 a 12,000 usuarios concurrentes.

## 1. Arquitectura de Despliegue (AWS)

Según el diseño propuesto:
- **Broker de Distribución (UI/Linkage)**: Implementado mediante un **AWS Application Load Balancer (ALB)**. Estará expuesto a internet y distribuirá las peticiones (GET de consumo) entre los servidores.
- **Manejador de Reportes**: Implementado con instancias **AWS EC2**. Para soportar 12,000 usuarios recurrentes se recomienda usar un Auto Scaling Group (ASG) configurado con instancias optimizadas para computo o uso general (ej: `c5.xlarge` o `m5.xlarge`). Aquí corre la app de Django con Gunicorn + Nginx.
- **Persistencia Reportes (Data Access)**: Implementado como un clúster o instancia principal de **AWS RDS (PostgreSQL)**, preferiblemente instancias tipo `db.m5.large` o `db.r5.xlarge` para aguantar altas consultas recurrentes con índices definidos en los timestamps y el campo de área.

## 2. Puesta en marcha de la Aplicación Django en EC2

En tus instancias EC2 debes clonar este código (o pasarlo vía CI/CD) y realizar los siguientes pasos de configuración inicial:

1. Instalar dependencias del sistema y Python (Python 3.10+, PostgreSQL client, Nginx):
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv python3-dev libpq-dev postgresql postgresql-contrib nginx curl
   ```

2. Configurar Entorno Virtual e instalar dependencias:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Variables de Entorno (`.env`):
   Crea un archivo `.env` en la raíz del proyecto (junto a `manage.py`):
   ```env
   DEBUG=False
   SECRET_KEY=tu_clave_secreta_aqui
   RDS_DB_NAME=postgres
   RDS_USERNAME=tu_usuario
   RDS_PASSWORD=tu_password
   RDS_HOSTNAME=ruta.cluster-rXXXXX.us-east-1.rds.amazonaws.com
   RDS_PORT=5432
   CONN_MAX_AGE=600  # Fundamental habilitar connection pooling en Django para 12k concurrentes
   ```

4. Ejecutar Migraciones (Sólo se hace en 1 nodo):
   ```bash
   python3 manage.py makemigrations reports
   python3 manage.py migrate
   ```

5. Correr con Gunicorn (ejemplo en bash para Systemd):
   Para aguantar alta concurrencia usarás Gunicorn con Workers tipo gevent o hilos altos.
   ```bash
   gunicorn --workers 9 --threads 4 cloud_reports.wsgi:application --bind 0.0.0.0:8000
   ```

## 3. Plan de Pruebas (JMeter)

Se adjuntó el archivo **`jmeter_test_plan.jmx`**.

- **Configuración:** Grupo de hilos (12,000 threads).
- **Ramp-up:** 60 segundos.
- **Duración Total (Duration):** 120 segundos (Para garantizar que llegue a los 12,000 y se mantenga ahí los 60 segundos requeridos por un minuto).
- **Endpoint a golpear:** `GET http://<DNS_DEL_LOAD_BALANCER_AWS>/api/reports/consumption-by-area/`

> **Nota para el Cliente de Carga**: Se recomienda que instales JMeter en otra instancia potente dentro de la misma VPC (EC2 `c5.2xlarge`) o la dividas en varios inyectores distribuidos, debido a que correr 12,000 hilos desde una máquina local o un nodo pequeño creará un cuello de botella en el lado del inyector, y no en los servidores que vas a probar.
