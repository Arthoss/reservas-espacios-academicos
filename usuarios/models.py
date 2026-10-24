from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class UsuarioManager(UserManager):
	def create_superuser(self, username, email=None, password=None, **extra_fields):
		extra_fields['rol'] = Usuario.Rol.ADMINISTRADOR
		return super().create_superuser(
			username,
			email=email,
			password=password,
			**extra_fields,
		)


class Usuario(AbstractUser):
	class Rol(models.TextChoices):
		SOLICITANTE = 'solicitante', 'Solicitante'
		ADMINISTRADOR = 'administrador', 'Administrador'

	rol = models.CharField(
		max_length=20,
		choices=Rol.choices,
		default=Rol.SOLICITANTE,
	)

	objects = UsuarioManager()
