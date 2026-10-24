from django.urls import path

from .views import DisponibilidadView, ReservaCreateView


app_name = 'reservas'

urlpatterns = [
    path('', ReservaCreateView.as_view(), name='crear'),
    path('disponibilidad/', DisponibilidadView.as_view(), name='disponibilidad'),
]