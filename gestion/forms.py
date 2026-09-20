from django import forms
from django.contrib.auth.hashers import make_password

from .models import Capa, Capacitacion, Documento, Hallazgo, Usuario


class LoginForm(forms.Form):
    correo = forms.CharField(label='Usuario')
    contrasena = forms.CharField(label='Contraseña', widget=forms.PasswordInput)


class UsuarioForm(forms.ModelForm):
    contrasena = forms.CharField(label='Contraseña', widget=forms.PasswordInput, required=False)

    class Meta:
        model = Usuario
        fields = ['nombre', 'cargo', 'area', 'correo', 'rol', 'estado']
        labels = {'rol': 'Rol', 'estado': 'Activo'}

    def save(self, commit=True):
        usuario = super().save(commit=False)
        contrasena = self.cleaned_data.get('contrasena')
        if contrasena:
            usuario.contrasena_hash = make_password(contrasena)
        if commit:
            usuario.save()
        return usuario


class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['nombre', 'codigo', 'version', 'estado', 'archivo']
        labels = {'nombre': 'Nombre', 'codigo': 'Código', 'version': 'Versión', 'estado': 'Estado', 'archivo': 'Archivo PDF o Word'}


class HallazgoForm(forms.ModelForm):
    class Meta:
        model = Hallazgo
        fields = ['descripcion', 'area', 'responsable', 'estado', 'fecha']
        widgets = {'fecha': forms.DateInput(attrs={'type': 'date'})}


class CapaForm(forms.ModelForm):
    class Meta:
        model = Capa
        fields = ['hallazgo', 'accion', 'responsable', 'estado', 'fecha']
        widgets = {'fecha': forms.DateInput(attrs={'type': 'date'})}


class CapacitacionForm(forms.ModelForm):
    class Meta:
        model = Capacitacion
        fields = ['nombre', 'responsable', 'participantes', 'estado', 'fecha']
        widgets = {'fecha': forms.DateInput(attrs={'type': 'date'})}
