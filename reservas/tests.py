from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from unittest.mock import patch

from django.db import IntegrityError, close_old_connections, connections, transaction
from django.test import TransactionTestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from espacios.models import Espacio
from usuarios.models import Usuario

from .models import Reserva


class ReservasApiTests(APITestCase):
	@classmethod
	def setUpTestData(cls):
		cls.solicitante = Usuario.objects.create_user(
			username='solicitante-reservas',
			email='solicitante-reservas@example.com',
			password='Solicitante-Reservas-Password-123!',
		)
		cls.otro_solicitante = Usuario.objects.create_user(
			username='otro-solicitante-reservas',
			email='otro-solicitante-reservas@example.com',
			password='Otro-Reservas-Password-123!',
		)
		cls.admin = Usuario.objects.create_superuser(
			username='admin-reservas',
			email='admin-reservas@example.com',
			password='Admin-Reservas-Password-123!',
		)
		cls.espacio = Espacio.objects.create(
			nombre='Laboratorio de pruebas',
			tipo=Espacio.Tipo.LABORATORIO,
			capacidad=20,
		)

	def setUp(self):
		self.reservas_url = reverse('reservas:crear')
		self.disponibilidad_url = reverse('reservas:disponibilidad')

	def intervalo_futuro(self, offset_hours=2):
		inicio = timezone.now() + timedelta(hours=offset_hours)
		return inicio, inicio + timedelta(hours=1)

	def payload(self, inicio=None, fin=None, espacio=None):
		if inicio is None or fin is None:
			inicio, fin = self.intervalo_futuro()
		return {
			'espacio': espacio or self.espacio.pk,
			'inicio': inicio.isoformat(),
			'fin': fin.isoformat(),
			'motivo': 'Actividad académica de prueba',
		}

	def consultar_disponibilidad(self, inicio, fin):
		return self.client.get(
			self.disponibilidad_url,
			{
				'espacio': self.espacio.pk,
				'inicio': inicio.isoformat(),
				'fin': fin.isoformat(),
			},
		)

	def test_solicitud_valida_crea_reserva_pendiente(self):
		self.client.force_authenticate(user=self.solicitante)
		inicio, fin = self.intervalo_futuro()

		response = self.client.post(
			self.reservas_url,
			self.payload(inicio, fin),
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		reserva = Reserva.objects.get(pk=response.data['id'])
		self.assertEqual(reserva.solicitante, self.solicitante)
		self.assertEqual(reserva.espacio, self.espacio)
		self.assertEqual(reserva.estado, Reserva.Estado.PENDIENTE)
		self.assertTrue(timezone.is_aware(reserva.inicio))
		self.assertTrue(timezone.is_aware(reserva.fin))

	def test_usuario_no_autenticado_no_crea_reserva(self):
		inicio, fin = self.intervalo_futuro()

		response = self.client.post(
			self.reservas_url,
			self.payload(inicio, fin),
			format='json',
		)

		self.assertIn(
			response.status_code,
			(status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
		)
		self.assertEqual(Reserva.objects.count(), 0)

	def test_administrador_no_puede_crear_reserva(self):
		self.client.force_authenticate(user=self.admin)
		inicio, fin = self.intervalo_futuro()

		response = self.client.post(
			self.reservas_url,
			self.payload(inicio, fin),
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
		self.assertEqual(Reserva.objects.count(), 0)

	def test_intervalo_vacio_o_invertido_es_rechazado(self):
		self.client.force_authenticate(user=self.solicitante)
		inicio, fin = self.intervalo_futuro()

		for invalid_start, invalid_end in ((inicio, inicio), (fin, inicio)):
			with self.subTest(inicio=invalid_start, fin=invalid_end):
				response = self.client.post(
					self.reservas_url,
					self.payload(invalid_start, invalid_end),
					format='json',
				)
				self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

		self.assertEqual(Reserva.objects.count(), 0)

	def test_inicio_pasado_es_rechazado(self):
		self.client.force_authenticate(user=self.solicitante)
		inicio = timezone.now() - timedelta(hours=2)
		fin = inicio + timedelta(hours=1)

		response = self.client.post(
			self.reservas_url,
			self.payload(inicio, fin),
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(Reserva.objects.count(), 0)

	def test_franja_disponible_se_informa_disponible(self):
		self.client.force_authenticate(user=self.solicitante)
		inicio, fin = self.intervalo_futuro()

		response = self.consultar_disponibilidad(inicio, fin)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertTrue(response.data['disponible'])

	def test_franja_ocupada_pendiente_o_aprobada_se_informa_ocupada(self):
		self.client.force_authenticate(user=self.solicitante)
		inicio, fin = self.intervalo_futuro()

		for estado in (Reserva.Estado.PENDIENTE, Reserva.Estado.APROBADA):
			with self.subTest(estado=estado):
				reserva = Reserva.objects.create(
					solicitante=self.solicitante,
					espacio=self.espacio,
					inicio=inicio,
					fin=fin,
					motivo='Franja ocupada',
					estado=estado,
				)
				response = self.consultar_disponibilidad(inicio, fin)
				self.assertEqual(response.status_code, status.HTTP_200_OK)
				self.assertFalse(response.data['disponible'])
				reserva.delete()

	def test_usuario_no_autenticado_no_consulta_disponibilidad(self):
		inicio, fin = self.intervalo_futuro()

		response = self.consultar_disponibilidad(inicio, fin)

		self.assertIn(
			response.status_code,
			(status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
		)
		self.assertNotIn('disponible', response.data)

	def test_solapamiento_con_reserva_pendiente_o_aprobada_es_rechazado(self):
		self.client.force_authenticate(user=self.solicitante)
		inicio, fin = self.intervalo_futuro()

		for estado in (Reserva.Estado.PENDIENTE, Reserva.Estado.APROBADA):
			with self.subTest(estado=estado):
				existente = Reserva.objects.create(
					solicitante=self.otro_solicitante,
					espacio=self.espacio,
					inicio=inicio,
					fin=fin,
					motivo='Reserva existente',
					estado=estado,
				)
				response = self.client.post(
					self.reservas_url,
					self.payload(inicio + timedelta(minutes=30), fin),
					format='json',
				)
				self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
				self.assertEqual(
					response.data,
					{'detail': 'El espacio no está disponible en esa franja.'},
				)
				existente.delete()

		self.assertEqual(Reserva.objects.count(), 0)

	def test_reservas_rechazadas_o_canceladas_no_ocupan_franja(self):
		self.client.force_authenticate(user=self.solicitante)
		inicio, fin = self.intervalo_futuro()

		for estado in (Reserva.Estado.RECHAZADA, Reserva.Estado.CANCELADA):
			with self.subTest(estado=estado):
				existente = Reserva.objects.create(
					solicitante=self.otro_solicitante,
					espacio=self.espacio,
					inicio=inicio,
					fin=fin,
					motivo='Reserva no activa',
					estado=estado,
				)
				response = self.client.post(
					self.reservas_url,
					self.payload(inicio, fin),
					format='json',
				)

				self.assertEqual(response.status_code, status.HTTP_201_CREATED)
				Reserva.objects.get(pk=response.data['id']).delete()
				existente.delete()

	def test_restriccion_postgresql_rechaza_solapamiento_activo(self):
		inicio, fin = self.intervalo_futuro()
		Reserva.objects.create(
			solicitante=self.solicitante,
			espacio=self.espacio,
			inicio=inicio,
			fin=fin,
			motivo='Primera reserva',
		)

		with self.assertRaises(IntegrityError):
			with transaction.atomic():
				Reserva.objects.create(
					solicitante=self.otro_solicitante,
					espacio=self.espacio,
					inicio=inicio + timedelta(minutes=1),
					fin=fin + timedelta(minutes=1),
					motivo='Solapamiento directo',
				)

		self.assertEqual(Reserva.objects.count(), 1)

	@patch(
		'reservas.views.ReservaCreateSerializer.create',
		side_effect=IntegrityError('simulated constraint conflict'),
	)
	def test_error_integridad_devuelve_conflicto_sin_guardar_reserva(self, _):
		self.client.force_authenticate(user=self.solicitante)
		inicio, fin = self.intervalo_futuro()

		response = self.client.post(
			self.reservas_url,
			self.payload(inicio, fin),
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
		self.assertEqual(
			response.data,
			{'detail': 'El espacio no está disponible en esa franja.'},
		)
		self.assertEqual(Reserva.objects.count(), 0)

	def test_reservas_consecutivas_son_aceptadas(self):
		self.client.force_authenticate(user=self.solicitante)
		inicio, fin = self.intervalo_futuro()
		Reserva.objects.create(
			solicitante=self.otro_solicitante,
			espacio=self.espacio,
			inicio=inicio,
			fin=fin,
			motivo='Primera franja',
		)

		response = self.client.post(
			self.reservas_url,
			self.payload(fin, fin + timedelta(hours=1)),
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Reserva.objects.count(), 2)

	def test_espacio_inactivo_no_acepta_reserva(self):
		self.client.force_authenticate(user=self.solicitante)
		self.espacio.activo = False
		self.espacio.save(update_fields=['activo'])
		inicio, fin = self.intervalo_futuro()

		response = self.client.post(
			self.reservas_url,
			self.payload(inicio, fin),
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
		self.assertEqual(
			response.data,
			{'detail': 'El espacio no está disponible en esa franja.'},
		)
		self.assertEqual(Reserva.objects.count(), 0)


class ReservaConcurrentCreationTests(TransactionTestCase):
	reset_sequences = True

	def setUp(self):
		self.users = [
			Usuario.objects.create_user(
				username=f'concurrente-{index}',
				email=f'concurrente-{index}@example.com',
				password='Concurrente-Password-123!',
			)
			for index in (1, 2)
		]
		self.espacio = Espacio.objects.create(
			nombre='Laboratorio concurrente',
			tipo=Espacio.Tipo.LABORATORIO,
			capacidad=16,
		)
		self.inicio = timezone.now() + timedelta(hours=5)
		self.fin = self.inicio + timedelta(hours=1)
		self.barrier = Barrier(2)

	def enviar_solicitud(self, user_id):
		close_old_connections()
		try:
			database = connections['default']
			with database.cursor() as cursor:
				cursor.execute('SELECT pg_backend_pid()')
				backend_pid = cursor.fetchone()[0]

			user = Usuario.objects.get(pk=user_id)
			client = APIClient()
			client.force_authenticate(user=user)
			self.barrier.wait(timeout=10)
			response = client.post(
				reverse('reservas:crear'),
				{
					'espacio': self.espacio.pk,
					'inicio': self.inicio.isoformat(),
					'fin': self.fin.isoformat(),
					'motivo': 'Solicitud concurrente',
				},
				format='json',
			)
			return response.status_code, backend_pid
		finally:
			connections['default'].close()
			close_old_connections()

	def test_dos_solicitudes_simultaneas_crean_exactamente_una_reserva(self):
		with ThreadPoolExecutor(max_workers=2) as executor:
			results = list(executor.map(
				self.enviar_solicitud,
				[user.pk for user in self.users],
			))

		status_codes = [status_code for status_code, _ in results]
		backend_pids = {backend_pid for _, backend_pid in results}

		self.assertEqual(len(backend_pids), 2)
		self.assertCountEqual(
			status_codes,
			[status.HTTP_201_CREATED, status.HTTP_409_CONFLICT],
		)
		self.assertEqual(
			Reserva.objects.filter(
				espacio=self.espacio,
				estado=Reserva.Estado.PENDIENTE,
			).count(),
			1,
		)
