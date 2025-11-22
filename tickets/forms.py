from django import forms
from .models import TicketMessage

class MessageForm(forms.ModelForm):
    class Meta:
        model = TicketMessage
        fields = ['message', 'attachment']