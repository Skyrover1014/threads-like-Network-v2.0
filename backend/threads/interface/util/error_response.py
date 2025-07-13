from rest_framework.response import Response

def error_response(message, type_name ="Unknown Error", code = 500, source="unknown"):
    return Response({
        "error": {
            "type": type_name,
            "message": str(message),
            "code":code
        }
    }, status=code)

