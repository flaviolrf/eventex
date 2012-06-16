# coding: utf-8

from django import forms
from .models import Subscription 
from django.contrib.localflavor.br.forms import BRCPFField, BRPhoneNumberField



class SubscriptionForm(forms.ModelForm):
	class Meta:
		model = Subscription
		exclude = ('paid',)
	cpf = BRCPFField(max_length=11, required=True)
	phone = BRPhoneNumberField()

