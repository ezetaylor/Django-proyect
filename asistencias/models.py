from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Curso(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Alumno(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"

class TipoAsistencia(models.Model):
    descripcion = models.CharField(max_length=50, unique=True)
    valor = models.FloatField()

    def __str__(self):
        return self.descripcion

class Asistencia(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    fecha = models.DateField()
    tipo_asistencia = models.ForeignKey(TipoAsistencia, on_delete=models.SET_NULL, null=True)
    observacion = models.TextField(blank=True)

    def __str__(self):
        return f"{self.alumno} - {self.fecha}"
    
class CursoAsignado(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.usuario.username} → {self.curso.nombre}"

