from django import forms
from .models import Report


# not used right now
class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('file_name', )