"""Formulaires de l'application core."""
from django import forms


class ContactForm(forms.Form):
    """Formulaire de contact avec validation complète."""

    SUBJECTS = [
        ('general', 'Question générale'),
        ('bug', 'Rapport de bug'),
        ('collab', 'Collaboration recherche'),
        ('api', 'Accès API'),
        ('partner', 'Partenariat agricole'),
        ('other', 'Autre'),
    ]

    name = forms.CharField(
        max_length=100,
        label='Nom complet',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre nom',
        })
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'vous@exemple.com',
        })
    )
    organization = forms.CharField(
        max_length=150,
        required=False,
        label='Organisation',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre établissement',
        })
    )
    subject = forms.ChoiceField(
        choices=SUBJECTS,
        label='Objet',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    message = forms.CharField(
        label='Message',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Décrivez votre demande en détail...',
            'rows': 6,
        })
    )
