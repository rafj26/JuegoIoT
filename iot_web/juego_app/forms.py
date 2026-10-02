"""Formularios de la version web."""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from juego_app.models import Usuario


class FormularioBootstrapMixin:
    """Agrega las clases CSS de Bootstrap a todos los campos."""

    def __init__(self, *args, **kwargs):
        """Inicializa el formulario y aplica estilos."""
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.widget.attrs.setdefault("class", "form-control")


class RegistroForm(FormularioBootstrapMixin, UserCreationForm):
    """Registro de un nuevo usuario."""

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ("username", "nombre_publico", "email")


class LoginForm(FormularioBootstrapMixin, AuthenticationForm):
    """Inicio de sesion."""


class PerfilForm(FormularioBootstrapMixin, forms.ModelForm):
    """Edicion de los datos publicos del usuario."""

    class Meta:
        model = Usuario
        fields = ("nombre_publico", "email")


class DecisionForm(forms.Form):
    """Alertas que el jugador decide atender en la ronda."""

    alertas = forms.TypedMultipleChoiceField(coerce=int, required=False,
                                             widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, total_alertas=0, **kwargs):
        """Crea una opcion por cada alerta de la ronda."""
        super().__init__(*args, **kwargs)
        self.fields["alertas"].choices = [(i, str(i)) for i in range(1, total_alertas + 1)]
