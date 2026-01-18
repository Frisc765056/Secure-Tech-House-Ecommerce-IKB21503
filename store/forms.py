from django import forms
from django.core.validators import RegexValidator

# --- REQUIREMENT B.1: INPUT VALIDATION & SANITIZATION ---
# This form uses a Strict Allowlist. It only allows alphanumeric characters.
# It explicitly blocks symbols like <, >, /, script, alert, etc.
class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9\s\-_]+$',
                message="Security Alert: Invalid characters detected. Only letters, numbers, spaces, hyphens, and underscores are allowed.",
                code='invalid_search'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            # UPDATED PLACEHOLDER:
            'placeholder': 'Search for hardware (e.g. RAM, GPU)...',
        })
    )

    # Clean method for extra sanitization (Double Check)
    def clean_query(self):
        data = self.cleaned_data.get('query', '')
        # Basic strip of leading/trailing whitespace
        return data.strip()