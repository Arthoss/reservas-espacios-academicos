from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, serializers, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from espacios.models import Espacio
from usuarios.permissions import IsRequester

from .models import Reserva


class ReservaCreateSerializer(serializers.ModelSerializer):
	class Meta:
		model = Reserva
		fields = ('id', 'espacio', 'inicio', 'fin', 'motivo', 'estado')
		read_only_fields = ('id', 'estado')

	def validate_motivo(self, value):
		if not value.strip():
			raise serializers.ValidationError('El motivo es obligatorio.')
		return value.strip()

	def validate(self, attrs):
		inicio = attrs['inicio']
		fin = attrs['fin']

		if inicio >= fin:
			raise serializers.ValidationError(
				{'fin': 'La fecha de fin debe ser posterior al inicio.'}
			)
		if inicio <= timezone.now():
			raise serializers.ValidationError(
				{'inicio': 'La fecha de inicio debe ser futura.'}
			)
		return attrs


class DisponibilidadSerializer(serializers.Serializer):
	espacio = serializers.IntegerField(min_value=1)
	inicio = serializers.DateTimeField()
	fin = serializers.DateTimeField()

	def validate(self, attrs):
		if attrs['inicio'] >= attrs['fin']:
			raise serializers.ValidationError(
				{'fin': 'La fecha de fin debe ser posterior al inicio.'}
			)
		return attrs


def availability_conflict():
	return Response(
		{'detail': 'El espacio no está disponible en esa franja.'},
		status=status.HTTP_409_CONFLICT,
	)


def has_active_overlap(espacio, inicio, fin):
	return Reserva.objects.filter(
		espacio=espacio,
		estado__in=[Reserva.Estado.PENDIENTE, Reserva.Estado.APROBADA],
		inicio__lt=fin,
		fin__gt=inicio,
	).exists()


class ReservaCreateView(generics.GenericAPIView):
	serializer_class = ReservaCreateSerializer
	permission_classes = [IsRequester]

	def post(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		espacio_id = serializer.validated_data['espacio'].pk
		inicio = serializer.validated_data['inicio']
		fin = serializer.validated_data['fin']

		try:
			with transaction.atomic():
				try:
					espacio = Espacio.objects.select_for_update().get(
						pk=espacio_id
					)
				except Espacio.DoesNotExist as exc:
					raise NotFound('El espacio no existe.') from exc

				if not espacio.activo or has_active_overlap(
					espacio,
					inicio,
					fin,
				):
					return availability_conflict()

				reserva = serializer.save(
					solicitante=request.user,
					espacio=espacio,
					estado=Reserva.Estado.PENDIENTE,
				)
		except IntegrityError:
			return availability_conflict()

		return Response(
			self.get_serializer(reserva).data,
			status=status.HTTP_201_CREATED,
		)


class DisponibilidadView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		serializer = DisponibilidadSerializer(data=request.query_params)
		serializer.is_valid(raise_exception=True)
		data = serializer.validated_data
		espacio = get_object_or_404(Espacio, pk=data['espacio'])
		disponible = espacio.activo and not has_active_overlap(
			espacio,
			data['inicio'],
			data['fin'],
		)

		return Response(
			{
				'espacio': espacio.pk,
				'inicio': data['inicio'],
				'fin': data['fin'],
				'disponible': disponible,
			}
		)

# Create your views here.
