from django import forms
from .models import Curso

class CursoFechaForm(forms.Form):
    curso = forms.ModelChoiceField(
        queryset=None,  # se setea en __init__
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    fecha = forms.DateField(
    widget=forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control'
            })
        )


    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        if usuario:
            self.fields['curso'].queryset = Curso.objects.filter(cursoasignado__usuario=usuario)