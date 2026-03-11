from django import forms
from .models import Lead, ActiveOrder


class ContactForm(forms.ModelForm):
    """Форма обратной связи"""

    class Meta:
        model = Lead
        fields = ['name', 'company', 'email', 'phone', 'project_type', 'budget', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Ваше имя',
                'class': 'form-control'
            }),
            'company': forms.TextInput(attrs={
                'placeholder': 'Компания',
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email',
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Телефон',
                'class': 'form-control'
            }),
            'message': forms.Textarea(attrs={
                'placeholder': 'Расскажите о задаче, KPI и сроках',
                'rows': 5,
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].required = False
        self.fields['email'].required = False
        self.fields['phone'].required = False
        self.fields['project_type'].required = False
        self.fields['budget'].required = False

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        phone = cleaned_data.get('phone')

        if not email and not phone:
            raise forms.ValidationError("Необходимо указать хотя бы один способ связи (Телефон или Email)")
        
        return cleaned_data


class ActiveOrderForm(forms.ModelForm):
    class Meta:
        model = ActiveOrder
        fields = ['title', 'description', 'status']
