from django.urls import path
from .views import ConsumptionByAreaView

urlpatterns = [
    path('consumption-by-area/', ConsumptionByAreaView.as_view(), name='consumption-by-area'),
]
