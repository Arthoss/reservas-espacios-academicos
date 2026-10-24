from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Usuario


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[])
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = Usuario
        fields = ('username', 'email', 'password')

    def validate_email(self, value):
        normalized_email = value.strip().lower()
        if Usuario.objects.filter(email__iexact=normalized_email).exists():
            raise serializers.ValidationError(
                'Ya existe una cuenta con este correo electrónico.'
            )
        return normalized_email

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return Usuario.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            rol=Usuario.Rol.SOLICITANTE,
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False, write_only=True)


class RoleChangeSerializer(serializers.Serializer):
    rol = serializers.ChoiceField(choices=Usuario.Rol.choices)