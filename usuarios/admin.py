from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
	fieldsets = UserAdmin.fieldsets + (
		('Rol', {'fields': ('rol',)}),
	)
	add_fieldsets = UserAdmin.add_fieldsets + (
		('Rol', {'fields': ('rol',)}),
	)
	list_display = (*UserAdmin.list_display, 'rol')
