from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Curso, Alumno, TipoAsistencia, Asistencia, CursoAsignado

# Re-registrar el modelo User con search_fields para que funcione el autocompletado
admin.site.unregister(User)

class CustomUserAdmin(UserAdmin):
    search_fields = ['username', 'email', 'first_name', 'last_name']

admin.site.register(User, CustomUserAdmin)

# Admin para Curso
class CursoAdmin(admin.ModelAdmin):
    search_fields = ['nombre']

admin.site.register(Curso, CursoAdmin)

# Admins para el resto
admin.site.register(Alumno)
admin.site.register(TipoAsistencia)
admin.site.register(Asistencia)

# Admin con autocomplete_fields
class CursoAsignadoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'curso')
    list_filter = ('curso',)
    search_fields = ('usuario__username', 'curso__nombre')
    autocomplete_fields = ['usuario', 'curso']

admin.site.register(CursoAsignado, CursoAsignadoAdmin)
