from django.db.models import Sum, Avg
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import CloudResourceConsumption

class ConsumptionByAreaView(APIView):
    """
    View to retrieve consumption analysis grouped by area.
    This simulates the critical 'Análisis de consumo por área' query mentioned in ASR 1.
    """
    
    # Optional: We could cache this if it doesn't need to be perfectly real-time,
    # but to strictly test the DB limits, we'll hit the DB.
    def get(self, request, *args, **kwargs):
        # A typical complex query: aggregate consumption value and cost by area
        try:
            # Doing an aggregate query forces DB computation
            analysis = CloudResourceConsumption.objects.values('area__name').annotate(
                total_consumption=Sum('consumption_value'),
                total_cost=Sum('cost'),
                avg_consumption=Avg('consumption_value')
            )
            
            # Convert QuerySet to list of dicts for JSON response
            results = list(analysis)
            
            return Response({"status": "success", "data": results}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"status": "error", "message": f"Server encountered an error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
