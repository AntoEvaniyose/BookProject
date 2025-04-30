from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
 
# 200: Fetch operations like GET.
def custom200(message, data=None):
    return Response(
        {
            "status": "Success",
            "status_code": 200,
            "message": message,
            "data": data if data is not None else {},
        },
        status=status.HTTP_200_OK,
    )
 
 
# 404: Invalid endpoint or missing resource.
def custom404(request,message):
    return Response(
        {
            "status": "Failed 'Not Found'.",
            "status_code": 404,
            "message": message,
        },
        status=status.HTTP_404_NOT_FOUND,
    )
 