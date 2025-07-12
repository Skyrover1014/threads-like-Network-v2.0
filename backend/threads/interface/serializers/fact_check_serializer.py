from rest_framework import serializers

class FactCheckSerializer(serializers.Serializer):
    content = serializers.CharField()
    prompt = serializers.CharField( allow_null = True, required = False )
   