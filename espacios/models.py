from django.db import models
from django.core.validators import MinValueValidator


class Espacio(models.Model):
	class Tipo(models.TextChoices):
		LABORATORIO = 'laboratorio', 'Laboratorio'
		AUDITORIO = 'auditorio', 'Auditorio'
		SALA_COMPUTO = 'sala_computo', 'Sala de cómputo'

	nombre = models.CharField(max_length=120)
	tipo = models.CharField(max_length=20, choices=Tipo.choices)
	capacidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
	activo = models.BooleanField(default=True)

	class Meta:
		ordering = ['nombre', 'id']

	def __str__(self):
		return self.nombre
