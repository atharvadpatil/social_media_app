from django import forms

from .models import Profile

class ProfileModelForm(forms.ModelForm):
    """Form definition for ProfileModel."""

    class Meta:
        """Meta definition for ProfileModelform."""

        model = Profile
        fields = ('first_name','last_name', 'bio', 'email', 'country', 'avatar')
        
