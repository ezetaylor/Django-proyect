import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Curso, Alumno, Asistencia, TipoAsistencia, CursoAsignado
from .forms import CursoFechaForm
from django import forms
from django.core.files.storage import default_storage
from io import StringIO  # 💡 necesario para manejar texto limpio
from datetime import date, datetime
from django.http import HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.contrib import messages






# Create your views here.
@login_required
def index(request):
    return render(request, 'index.html')

@login_required
def panel_asistencias(request):
    # Lógica de tu vista
    return render(request, 'panel.html', {...})

@login_required
def panel_preceptor(request):
    # Podés pasar más datos al contexto según necesites
    contexto = {
        'usuario': request.user,
    }
    return render(request, 'panel_preceptor.html', contexto)

@login_required
def cargar_lista_alumnos(request):
    # lógica de la vista
    return render(request, 'cargar_lista_alumnos.html')

@login_required
def modificar_asistencia(request):
    return render(request, 'modificar_asistencia.html')

class AlumnoForm(forms.ModelForm):
    class Meta:
        model = Alumno
        fields = ['nombre', 'apellido', 'curso']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'curso': forms.Select(attrs={'class': 'form-select'}),
        }

@login_required
def agregar_alumno(request):
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')  # o a lista de alumnos
    else:
        form = AlumnoForm()
    return render(request, 'agregar_alumno.html', {'form': form})

@login_required
def importar_alumnos_csv(request):
    agregados = 0
    existentes = 0

    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        
        # 🔄 Elimina BOM automáticamente
        contenido = archivo.read().decode('utf-8-sig')
        reader = csv.DictReader(StringIO(contenido), delimiter=';')

        for fila in reader:
            nombre = fila['nombre'].strip()
            apellido = fila['apellido'].strip()
            nombre_curso = fila['curso'].strip()

            curso_obj, _ = Curso.objects.get_or_create(nombre=nombre_curso)

            existe = Alumno.objects.filter(
                nombre=nombre,
                apellido=apellido,
                curso=curso_obj
            ).exists()

            if existe:
                existentes += 1
            else:
                Alumno.objects.create(
                    nombre=nombre,
                    apellido=apellido,
                    curso=curso_obj
                )
                agregados += 1

        return render(request, 'importar_alumnos.html', {
            'resumen': {
                'agregados': agregados,
                'existentes': existentes,
            }
        })

    return render(request, 'importar_alumnos.html')

@login_required
def registrar_asistencia(request, curso_id, fecha):
    curso = Curso.objects.get(id=curso_id)
    fecha = datetime.strptime(fecha, '%Y-%m-%d').date() 
    alumnos = Alumno.objects.filter(curso=curso)
    tipos = TipoAsistencia.objects.all()
    asistencias_existentes = Asistencia.objects.filter(fecha=fecha, alumno__curso=curso)
    print("Fecha recibida:", fecha)
    print("Asistencias encontradas:", asistencias_existentes.count())
    for a in asistencias_existentes:
        print(f"{a.alumno.apellido}, {getattr(a.tipo_asistencia, 'descripcion', 'Sin descripción')}, {a.fecha}")

    # Juntamos (alumno, asistencia) para cada fila
    filas = []
    for alumno in alumnos:
        asistencia = next((a for a in asistencias_existentes if a.alumno.id == alumno.id), None)
        filas.append((alumno, asistencia))

    if request.method == 'POST':
        for alumno, asistencia in filas:
            tipo_id = request.POST.get(f"tipo_{alumno.id}")
            observacion = request.POST.get(f"observacion_{alumno.id}", "").strip()
            tipo = TipoAsistencia.objects.get(id=tipo_id)

            Asistencia.objects.update_or_create(
                alumno=alumno,
                fecha=fecha,
                defaults={
                    'tipo_asistencia': tipo,
                    'observacion': observacion
                }
            )

        return redirect('dashboard')

    return render(request, 'registrar_asistencia.html', {
        'curso': curso,
        'fecha': fecha,
        'curso_id': curso.id,  # 👈 esto
        'fecha_str': fecha.strftime('%Y-%m-%d'),  # 👈 y esto
        'tipos': tipos,
        'filas': filas,

    })


@login_required
def seleccionar_curso_fecha(request):
    if request.method == 'POST':
        form = CursoFechaForm(request.POST, usuario=request.user)
        if form.is_valid():
            curso_id = form.cleaned_data['curso'].id
            fecha = form.cleaned_data['fecha']
            return redirect('registrar_asistencia', curso_id=curso_id, fecha=fecha)
    else:
        form = CursoFechaForm(usuario=request.user)

    return render(request, 'seleccionar_curso_fecha.html', {'form': form})


@login_required
def reporte_asistencias(request):
    curso_id = request.GET.get('curso_id')
    año = request.GET.get('año')
    mes = request.GET.get('mes')

    if not curso_id or not año or not mes:
        return HttpResponseBadRequest("Faltan parámetros: curso_id, año o mes.")

    try:
        curso = get_object_or_404(Curso, id=int(curso_id))
        año = int(año)
        mes = int(mes)
    except ValueError:
        return HttpResponseBadRequest("Los parámetros deben ser números válidos.")
    
    alumnos = Alumno.objects.filter(curso=curso)
    cantidad_alumnos = alumnos.count()
    asistencias = Asistencia.objects.filter(
        alumno__curso=curso,
        fecha__year=año,
        fecha__month=mes
    )

    reporte = []
    total_asistencias = 0.0
    total_inasistencias = 0.0

    for alumno in alumnos:
        registros = asistencias.filter(alumno=alumno)
        asistencia_valor = 0.0
        inasistencia_valor = 0.0

        for registro in registros:
            tipo = registro.tipo_asistencia
            if tipo:
                asistencia_valor += tipo.valor
                inasistencia_valor += (1 - tipo.valor)

        total_dias = asistencia_valor + inasistencia_valor
        total_asistencias += asistencia_valor
        total_inasistencias += inasistencia_valor

        reporte.append({
            'alumno': alumno,
            'asistencias': asistencia_valor,
            'inasistencias': inasistencia_valor,
            'total': total_dias
        })

    total_general = total_asistencias + total_inasistencias

    return render(request, 'reporte_asistencias_mensual.html', {
        'curso': curso,
        'mes': mes,
        'año': año,
        'reporte': reporte,
        'total_asistencias': total_asistencias,
        'total_inasistencias': total_inasistencias,
        'total_general': total_general,
        'dias_habiles': None,  # Se puede usar más adelante
        'cantidad_alumnos': cantidad_alumnos,
        'total_esperado': None  # Calculable desde el template o con JavaScript

    })


@login_required
def panel_preceptor(request):
    # Cursos del usuario
    cursos_asignados = CursoAsignado.objects.filter(usuario=request.user)

    # Meses disponibles (1 a 12 con nombre)
    meses = [(i, date(1900, i, 1).strftime('%B')) for i in range(1, 13)]

    # Años disponibles registrados en la base
    años_disponibles_raw = Asistencia.objects.dates('fecha', 'year')
    años_disponibles = [(a.year, str(a.year)) for a in años_disponibles_raw]

    # Mes y año actual del sistema
    ahora = datetime.now()
    mes_actual = ahora.month
    año_actual = ahora.year

    contexto = {
        'usuario': request.user,
        'cursos_asignados': cursos_asignados,
        'meses': meses,
        'años_disponibles': años_disponibles,
        'mes_actual': mes_actual,
        'año_actual': año_actual
    }

    return render(request, 'panel_preceptor.html', contexto)

@login_required
@require_POST
def eliminar_asistencias_dia(request):
    fecha = request.POST.get('fecha')
    curso_id = request.POST.get('curso_id')

    if not fecha or not curso_id:
        return HttpResponseBadRequest("Faltan datos para eliminar asistencias.")

    try:
        curso = Curso.objects.get(id=curso_id)
        fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
    except (Curso.DoesNotExist, ValueError):
        return HttpResponseBadRequest("Datos inválidos.")

    Asistencia.objects.filter(
        alumno__curso=curso,
        fecha=fecha_obj
    ).delete()

    messages.success(request, "Asistencias del día eliminadas correctamente.")
    return redirect('registrar_asistencia', curso_id=curso.id, fecha=str(fecha))