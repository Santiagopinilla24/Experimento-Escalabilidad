import random
from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from reports.models import Area, CloudResourceConsumption

class Command(BaseCommand):
    help = 'Puebla la base de datos con 15,000 registros de prueba para el experimento de escalabilidad.'

    def handle(self, *args, **kwargs):
        self.stdout.write('Eliminando datos anteriores...')
        CloudResourceConsumption.objects.all().delete()
        Area.objects.all().delete()
        
        self.stdout.write('Creando áreas...')
        areas = ['Ventas', 'Ingeniería', 'Recursos Humanos', 'Marketing', 'Soporte', 'Operaciones', 'Finanzas', 'TI']
        area_objs = []
        for name in areas:
            area_objs.append(Area(name=name))
        
        # Guardamos en la base de datos
        Area.objects.bulk_create(area_objs)
        saved_areas = list(Area.objects.all())

        self.stdout.write('Creando 15,000 registros de consumo en memoria...')
        resource_types = ['EC2', 'RDS', 'S3', 'Lambda', 'ElastiCache']
        consumptions = []
        now = timezone.now()
        
        # Crearemos lotes de registros para usar bulk_create (mucho más rápido y eficiente)
        total_records = 15000
        batch_size = 5000
        
        for i in range(total_records):
            consumptions.append(
                CloudResourceConsumption(
                    area=random.choice(saved_areas),
                    resource_type=random.choice(resource_types),
                    consumption_value=round(random.uniform(10.0, 5000.0), 4),
                    cost=round(random.uniform(5.0, 1000.0), 2),
                    timestamp=now - timedelta(days=random.randint(0, 365), hours=random.randint(0, 23))
                )
            )
            
            # Realizamos el volcado a RDS por lotes de 5000 para no consumir RAM eterna ni colapsar la base local
            if len(consumptions) >= batch_size:
                CloudResourceConsumption.objects.bulk_create(consumptions)
                self.stdout.write(f'  ... insertados {i + 1} registros')
                consumptions = []

        # Volcar el resto si sobran registros
        if consumptions:
            CloudResourceConsumption.objects.bulk_create(consumptions)

        self.stdout.write(self.style.SUCCESS('¡Base de datos llenada exitosamente con 15.000 registros listas para consultas pesadas!'))
