from django.contrib import admin

from .models import Espacio


@admin.register(Espacio)
class EspacioAdmin(admin.ModelAdmin):
	list_display = ('nombre', 'tipo', 'capacidad', 'activo')
	list_filter = ('tipo', 'activo')
	search_fields = ('nombre',)
