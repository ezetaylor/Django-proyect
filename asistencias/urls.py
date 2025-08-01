from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.panel_preceptor, name='dashboard'),
    path('registrar-asistencia/<int:curso_id>/<str:fecha>/', views.registrar_asistencia, name='registrar_asistencia'),
    
    # Vista para seleccionar curso y fecha (si existe)
    path('seleccionar-curso/', views.seleccionar_curso_fecha, name='seleccionar_curso'),
    path('agregar-alumno/', views.agregar_alumno, name='agregar_alumno'),
    path('importar-csv/', views.importar_alumnos_csv, name='importar_alumnos'),
    path('panel-preceptor/', views.panel_preceptor, name='panel_preceptor'),
    path('reporte_asistencias_mensual/', views.reporte_asistencias, name='reporte_asistencias_mensual'),
    path('eliminar_asistencias_dia/', views.eliminar_asistencias_dia, name='eliminar_asistencias_dia'),



    # aquí van más rutas de tu app...
]