from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Usuario
from .permissions import IsAdministrator
from .serializers import LoginSerializer, RegistrationSerializer, RoleChangeSerializer


_DUMMY_PASSWORD_HASH = make_password('not-a-real-password')
_INVALID_CREDENTIALS = {'detail': 'Correo o contraseña incorrectos.'}


class RegistrationView(generics.CreateAPIView):
	authentication_classes = []
	permission_classes = [AllowAny]
	serializer_class = RegistrationSerializer


class LoginView(APIView):
	authentication_classes = []
	permission_classes = [AllowAny]

	def post(self, request):
		serializer = LoginSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		email = serializer.validated_data['email']
		password = serializer.validated_data['password']
		account = Usuario.objects.filter(email__iexact=email).first()

		if account is None:
			check_password(password, _DUMMY_PASSWORD_HASH)
			authenticated_user = None
		else:
			authenticated_user = authenticate(
				request,
				username=account.username,
				password=password,
			)

		if authenticated_user is None:
			return Response(
				_INVALID_CREDENTIALS,
				status=status.HTTP_401_UNAUTHORIZED,
			)

		login(request, authenticated_user)
		return Response(
			{
				'id': authenticated_user.pk,
				'username': authenticated_user.username,
				'email': authenticated_user.email,
				'rol': authenticated_user.rol,
			}
		)


class RoleChangeView(APIView):
	permission_classes = [IsAdministrator]

	def patch(self, request, user_id):
		target = get_object_or_404(Usuario, pk=user_id)
		serializer = RoleChangeSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		target.rol = serializer.validated_data['rol']
		target.save(update_fields=['rol'])

		return Response({'id': target.pk, 'rol': target.rol})
