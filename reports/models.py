from django.db import models

class ResourceConsumption(models.fields.Field):
    pass # To be replaced with actual model, creating blank to avoid errors

class Area(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class CloudResourceConsumption(models.Model):
    """
    Simulates a materialized view or table with pre-aggregated 
    or raw consumption data by area.
    """
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='consumptions')
    resource_type = models.CharField(max_length=100, db_index=True)
    consumption_value = models.DecimalField(max_digits=15, decimal_places=4)
    cost = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['area', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.area.name} - {self.resource_type} - {self.timestamp.date()}"
