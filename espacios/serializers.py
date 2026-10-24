from rest_framework import serializers

from .models import Espacio


class EspacioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Espacio
        fields = ('id', 'nombre', 'tipo', 'capacidad', 'activo')
        read_only_fields = ('id',)
        extra_kwargs = {
            'nombre': {'allow_blank': False, 'trim_whitespace': True},
            'capacidad': {'min_value': 1},
        }