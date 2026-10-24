from datetime import timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone

from reservas.models import Reserva
from usuarios.models import Usuario

from .models import Espacio


class EspaciosApiTests(APITestCase):
	@classmethod
	def setUpTestData(cls):
		cls.admin = Usuario.objects.create_superuser(
			username='admin-espacios',
			email='admin-espacios@example.com',
			password='Admin-Espacios-Password-123!',
		)
		cls.solicitante = Usuario.objects.create_user(
			username='solicitante-espacios',
			email='solicitante-espacios@example.com',
			password='Solicitante-Password-123!',
		)
		cls.auditorio = Espacio.objects.create(
			nombre='Auditorio central',
			tipo=Espacio.Tipo.AUDITORIO,
			capacidad=120,
		)
		cls.laboratorio = Espacio.objects.create(
			nombre='Laboratorio de química',
			tipo=Espacio.Tipo.LABORATORIO,
			capacidad=24,
		)
		cls.inactivo = Espacio.objects.create(
			nombre='Sala fuera de servicio',
			tipo=Espacio.Tipo.SALA_COMPUTO,
			capacidad=18,
			activo=False,
		)

	def setUp(self):
		self.catalog_url = reverse('espacios:espacio-list')

	def test_usuario_autenticado_consulta_solo_espacios_activos(self):
		self.client.force_authenticate(user=self.solicitante)

		response = self.client.get(self.catalog_url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(
			{item['id'] for item in response.data},
			{self.auditorio.pk, self.laboratorio.pk},
		)

	def test_usuario_autenticado_filtra_catalogo_por_tipo(self):
		self.client.force_authenticate(user=self.solicitante)

		response = self.client.get(
			self.catalog_url,
			{'tipo': Espacio.Tipo.AUDITORIO},
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(
			[item['id'] for item in response.data],
			[self.auditorio.pk],
		)

	def test_usuario_no_autenticado_consulta_catalogo(self):
		for query_params in ({}, {'tipo': Espacio.Tipo.AUDITORIO}):
			with self.subTest(query_params=query_params):
				response = self.client.get(self.catalog_url, query_params)

				self.assertIn(
					response.status_code,
					(status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
				)

	def test_administrador_crea_espacio_valido(self):
		self.client.force_authenticate(user=self.admin)

		response = self.client.post(
			self.catalog_url,
			{
				'nombre': 'Sala de estudio',
				'tipo': Espacio.Tipo.SALA_COMPUTO,
				'capacidad': 30,
			},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertTrue(
			Espacio.objects.filter(
				pk=response.data['id'],
				activo=True,
				capacidad=30,
			).exists()
		)

	def test_administrador_desactiva_y_reactiva_espacio(self):
		self.client.force_authenticate(user=self.admin)
		detail_url = reverse('espacios:espacio-detail', args=[self.auditorio.pk])

		update_response = self.client.patch(
			detail_url,
			{'nombre': 'Auditorio actualizado', 'capacidad': 140},
			format='json',
		)

		self.assertEqual(update_response.status_code, status.HTTP_200_OK)
		self.auditorio.refresh_from_db()
		self.assertEqual(self.auditorio.nombre, 'Auditorio actualizado')
		self.assertEqual(self.auditorio.capacidad, 140)

		deactivate_response = self.client.patch(
			detail_url,
			{'activo': False},
			format='json',
		)

		self.assertEqual(deactivate_response.status_code, status.HTTP_200_OK)
		self.auditorio.refresh_from_db()
		self.assertFalse(self.auditorio.activo)
		self.assertEqual(self.auditorio.nombre, 'Auditorio actualizado')

		reactivate_response = self.client.patch(
			detail_url,
			{'activo': True},
			format='json',
		)

		self.assertEqual(reactivate_response.status_code, status.HTTP_200_OK)
		self.auditorio.refresh_from_db()
		self.assertTrue(self.auditorio.activo)

	def test_solicitante_no_crea_modifica_ni_elimina_espacios(self):
		self.client.force_authenticate(user=self.solicitante)
		detail_url = reverse('espacios:espacio-detail', args=[self.auditorio.pk])

		create_response = self.client.post(
			self.catalog_url,
			{
				'nombre': 'Espacio no autorizado',
				'tipo': Espacio.Tipo.AUDITORIO,
				'capacidad': 30,
			},
			format='json',
		)
		update_response = self.client.patch(
			detail_url,
			{'nombre': 'Nombre alterado'},
			format='json',
		)
		delete_response = self.client.delete(detail_url)

		self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)
		self.assertEqual(update_response.status_code, status.HTTP_403_FORBIDDEN)
		self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)
		self.auditorio.refresh_from_db()
		self.assertEqual(self.auditorio.nombre, 'Auditorio central')

	def test_administrador_no_guarda_datos_invalidos(self):
		self.client.force_authenticate(user=self.admin)
		invalid_payloads = (
			{'tipo': Espacio.Tipo.LABORATORIO, 'capacidad': 10},
			{
				'nombre': 'Tipo desconocido',
				'tipo': 'tipo_inexistente',
				'capacidad': 10,
			},
			{
				'nombre': 'Capacidad cero',
				'tipo': Espacio.Tipo.LABORATORIO,
				'capacidad': 0,
			},
		)

		for payload in invalid_payloads:
			with self.subTest(payload=payload):
				response = self.client.post(
					self.catalog_url,
					payload,
					format='json',
				)
				self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

		self.assertEqual(Espacio.objects.count(), 3)

	def test_administrador_elimina_espacio_sin_reservas(self):
		self.client.force_authenticate(user=self.admin)
		space = Espacio.objects.create(
			nombre='Sala temporal',
			tipo=Espacio.Tipo.SALA_COMPUTO,
			capacidad=12,
		)

		response = self.client.delete(
			reverse('espacios:espacio-detail', args=[space.pk])
		)

		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
		self.assertFalse(Espacio.objects.filter(pk=space.pk).exists())

	def test_eliminar_espacio_con_reserva_es_rechazado(self):
		self.client.force_authenticate(user=self.admin)
		inicio = timezone.now() + timedelta(days=1)
		reserva = Reserva.objects.create(
			solicitante=self.solicitante,
			espacio=self.auditorio,
			inicio=inicio,
			fin=inicio + timedelta(hours=1),
			motivo='Reserva que protege el espacio',
		)

		response = self.client.delete(
			reverse('espacios:espacio-detail', args=[self.auditorio.pk])
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertTrue(Espacio.objects.filter(pk=self.auditorio.pk).exists())
		self.assertTrue(Reserva.objects.filter(pk=reserva.pk).exists())

	def test_desactivar_espacio_conserva_reservas_y_bloquea_nuevas(self):
		inicio = timezone.now() + timedelta(days=2)
		reservas_existentes = [
			Reserva.objects.create(
				solicitante=self.solicitante,
				espacio=self.auditorio,
				inicio=inicio,
				fin=inicio + timedelta(hours=1),
				motivo='Reserva pendiente existente',
				estado=Reserva.Estado.PENDIENTE,
			),
			Reserva.objects.create(
				solicitante=self.solicitante,
				espacio=self.auditorio,
				inicio=inicio + timedelta(hours=2),
				fin=inicio + timedelta(hours=3),
				motivo='Reserva aprobada existente',
				estado=Reserva.Estado.APROBADA,
			),
		]
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(
			reverse('espacios:espacio-detail', args=[self.auditorio.pk]),
			{'activo': False},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.auditorio.refresh_from_db()
		self.assertFalse(self.auditorio.activo)
		for reserva in reservas_existentes:
			reserva.refresh_from_db()
			self.assertTrue(Reserva.objects.filter(pk=reserva.pk).exists())
		self.assertEqual(
			[reserva.estado for reserva in reservas_existentes],
			[Reserva.Estado.PENDIENTE, Reserva.Estado.APROBADA],
		)

		self.client.force_authenticate(user=self.solicitante)
		nueva_inicio = inicio + timedelta(days=1)
		response = self.client.post(
			reverse('reservas:crear'),
			{
				'espacio': self.auditorio.pk,
				'inicio': nueva_inicio.isoformat(),
				'fin': (nueva_inicio + timedelta(hours=1)).isoformat(),
				'motivo': 'Nueva reserva tras desactivación',
			},
			format='json',
		)
		self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
