from django.urls import path

from .views import LoginView, RegistrationView, RoleChangeView


app_name = 'usuarios'

urlpatterns = [
    path('registro/', RegistrationView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('<int:user_id>/rol/', RoleChangeView.as_view(), name='cambiar-rol'),
]