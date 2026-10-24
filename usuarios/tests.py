import os
from types import SimpleNamespace
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Usuario
from .permissions import IsAdministrator


class UsuariosApiTests(TestCase):
	@classmethod
	def setUpTestData(cls):
		cls.admin = Usuario.objects.create_superuser(
			username='admin-test',
			email='admin-test@example.com',
			password='Admin-Strong-Password-123!',
		)
		cls.solicitante = Usuario.objects.create_user(
			username='solicitante-test',
			email='solicitante@example.com',
			password='Solicitante-Strong-Password-123!',
		)
		cls.otro_solicitante = Usuario.objects.create_user(
			username='otro-solicitante-test',
			email='otro@example.com',
			password='Otro-Strong-Password-123!',
		)

	def setUp(self):
		self.client = APIClient()

	def test_registro_valido_crea_solicitante(self):
		response = self.client.post(
			'/api/usuarios/registro/',
			{
				'username': 'nuevo-solicitante',
				'email': 'Nuevo.Solicitante@example.com',
				'password': 'Nuevo-Solicitante-Password-123!',
			},
			format='json',
		)

		self.assertEqual(response.status_code, 201)
		account = Usuario.objects.get(username='nuevo-solicitante')
		self.assertEqual(account.email, 'nuevo.solicitante@example.com')
		self.assertEqual(account.rol, Usuario.Rol.SOLICITANTE)
		self.assertTrue(account.is_active)
		self.assertNotEqual(account.password, 'Nuevo-Solicitante-Password-123!')

	def test_registro_con_correo_existente_informa_identidad_en_uso(self):
		response = self.client.post(
			'/api/usuarios/registro/',
			{
				'username': 'duplicado',
				'email': 'SOLICITANTE@example.com',
				'password': 'Duplicado-Password-123!',
			},
			format='json',
		)

		self.assertEqual(response.status_code, 400)
		self.assertIn('email', response.data)
		self.assertIn('Ya existe una cuenta', str(response.data['email']))
		self.assertFalse(Usuario.objects.filter(username='duplicado').exists())

	@patch.dict(os.environ, {'DJANGO_SUPERUSER_PASSWORD': 'Bootstrap-Password-123!'})
	def test_createsuperuser_crea_primer_administrador(self):
		Usuario.objects.filter(rol=Usuario.Rol.ADMINISTRADOR).delete()
		call_command(
			'createsuperuser',
			username='bootstrap-admin',
			email='bootstrap-admin@example.com',
			interactive=False,
			verbosity=0,
		)

		account = Usuario.objects.get(username='bootstrap-admin')
		self.assertEqual(account.rol, Usuario.Rol.ADMINISTRADOR)
		self.assertTrue(account.is_active)
		self.assertTrue(account.is_staff)
		self.assertTrue(account.is_superuser)

	def test_autenticacion_valida_inicia_sesion(self):
		response = self.client.post(
			'/api/usuarios/login/',
			{
				'email': 'SOLICITANTE@example.com',
				'password': 'Solicitante-Strong-Password-123!',
			},
			format='json',
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['rol'], Usuario.Rol.SOLICITANTE)
		self.assertIn('_auth_user_id', self.client.session)

	def test_autenticacion_fallida_no_distingue_correo_de_contrasena(self):
		unknown_email_response = self.client.post(
			'/api/usuarios/login/',
			{'email': 'inexistente@example.com', 'password': 'Incorrect-Password-123!'},
			format='json',
		)
		wrong_password_response = self.client.post(
			'/api/usuarios/login/',
			{'email': 'solicitante@example.com', 'password': 'Incorrect-Password-123!'},
			format='json',
		)

		self.assertEqual(unknown_email_response.status_code, 401)
		self.assertEqual(wrong_password_response.status_code, 401)
		self.assertEqual(unknown_email_response.data, wrong_password_response.data)

	def test_solicitante_no_puede_administrar_espacios(self):
		permission = IsAdministrator()
		request = SimpleNamespace(user=self.solicitante)

		self.assertFalse(permission.has_permission(request, view=None))

	def test_usuario_no_autenticado_no_accede_a_accion_protegida(self):
		response = self.client.patch(
			f'/api/usuarios/{self.otro_solicitante.pk}/rol/',
			{'rol': Usuario.Rol.ADMINISTRADOR},
			format='json',
		)

		self.assertIn(response.status_code, (401, 403))
		self.otro_solicitante.refresh_from_db()
		self.assertEqual(self.otro_solicitante.rol, Usuario.Rol.SOLICITANTE)

	def test_administrador_cambia_rol_y_permiso_se_aplica(self):
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(
			f'/api/usuarios/{self.solicitante.pk}/rol/',
			{'rol': Usuario.Rol.ADMINISTRADOR},
			format='json',
		)

		self.assertEqual(response.status_code, 200)
		self.solicitante.refresh_from_db()
		self.assertEqual(self.solicitante.rol, Usuario.Rol.ADMINISTRADOR)
		self.assertTrue(
			IsAdministrator().has_permission(
				SimpleNamespace(user=self.solicitante),
				view=None,
			)
		)

	def test_solicitante_no_cambia_rol_propio_ni_ajeno(self):
		self.client.force_authenticate(user=self.solicitante)

		for target in (self.solicitante, self.otro_solicitante):
			response = self.client.patch(
				f'/api/usuarios/{target.pk}/rol/',
				{'rol': Usuario.Rol.ADMINISTRADOR},
				format='json',
			)
			self.assertEqual(response.status_code, 403)

		self.solicitante.refresh_from_db()
		self.otro_solicitante.refresh_from_db()
		self.assertEqual(self.solicitante.rol, Usuario.Rol.SOLICITANTE)
		self.assertEqual(self.otro_solicitante.rol, Usuario.Rol.SOLICITANTE)
