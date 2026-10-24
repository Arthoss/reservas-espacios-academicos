from django.conf import settings
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import RangeOperators
from django.db import models
from django.db.models import F, Func, Q, Value


class Reserva(models.Model):
	class Estado(models.TextChoices):
		PENDIENTE = 'pendiente', 'Pendiente'
		APROBADA = 'aprobada', 'Aprobada'
		RECHAZADA = 'rechazada', 'Rechazada'
		CANCELADA = 'cancelada', 'Cancelada'

	solicitante = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.PROTECT,
		related_name='reservas',
	)
	espacio = models.ForeignKey(
		'espacios.Espacio',
		on_delete=models.PROTECT,
		related_name='reservas',
	)
	inicio = models.DateTimeField()
	fin = models.DateTimeField()
	motivo = models.TextField()
	estado = models.CharField(
		max_length=10,
		choices=Estado.choices,
		default=Estado.PENDIENTE,
	)

	class Meta:
		ordering = ['inicio', 'id']
		constraints = [
			models.CheckConstraint(
				condition=Q(inicio__lt=F('fin')),
				name='reserva_inicio_antes_fin',
			),
			ExclusionConstraint(
				name='reserva_sin_solapamiento_activo',
				expressions=[
					('espacio', RangeOperators.EQUAL),
					(
						Func(
							F('inicio'),
							F('fin'),
							Value('[)'),
							function='TSTZRANGE',
						),
						RangeOperators.OVERLAPS,
					),
				],
				condition=Q(estado__in=['pendiente', 'aprobada']),
			),
		]

	def __str__(self):
		return f'{self.espacio} ({self.inicio:%Y-%m-%d %H:%M})'
