from django import forms
from localflavor.ru.forms import RUPostalCodeField  # Импортируем поле для почтового индекса России
from .models import Order

class OrderCreateForm(forms.ModelForm):
    postal_code = RUPostalCodeField()  # Используем RUPostalCodeField для поля postal_code
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city']
