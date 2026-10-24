from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from usuarios.models import Usuario
from usuarios.permissions import IsAdministrator

from .models import Espacio
from .serializers import EspacioSerializer


class EspacioViewSet(viewsets.ModelViewSet):
	serializer_class = EspacioSerializer
	queryset = Espacio.objects.all()

	def get_permissions(self):
		if self.action in {'list', 'retrieve'}:
			return [IsAuthenticated()]
		return [IsAdministrator()]

	def get_queryset(self):
		queryset = Espacio.objects.all()
		user = self.request.user
		is_admin = (
			user.is_authenticated
			and user.rol == Usuario.Rol.ADMINISTRADOR
		)

		if not is_admin or self.action == 'list':
			queryset = queryset.filter(activo=True)

		tipo = self.request.query_params.get('tipo')
		if tipo:
			if tipo not in Espacio.Tipo.values:
				raise ValidationError({'tipo': 'Tipo de espacio no admitido.'})
			queryset = queryset.filter(tipo=tipo)

		return queryset
