from django import forms
from iptracker.models import *

class RecordForm(forms.Form):
  name = forms.CharField(max_length=255)
  type_choices = []
  choices = Domain.objects.all()
  for choice in choices:
    type_choices.append( (choice.id, choice.name) )
  domain = forms.TypedChoiceField(choices=type_choices)
  type = forms.TypedChoiceField(choices=Record.type_choices)
  content = forms.CharField()
  ttl = forms.CharField()
  comment = forms.CharField()

class DomainForm(forms.Form):
  name = forms.CharField(max_length=255)
  type = forms.TypedChoiceField(choices=Domain.type_choices)
  comment = forms.CharField()

class RangeForm(forms.Form):
  name = forms.CharField(max_length=255)
  start = forms.CharField()
  end = forms.CharField()
  comment = forms.CharField()

class AddRecordForm(forms.Form):
  type_choices = []
  choices = Domain.objects.all()
  for choice in choices:
    type_choices.append( (choice.id, choice.name) )
  name = forms.CharField(max_length=255)
  domain = forms.TypedChoiceField(choices=type_choices)
  type = forms.TypedChoiceField(choices=Record.type_choices)
  content = forms.CharField()
  ttl = forms.CharField()
  comment = forms.CharField()
