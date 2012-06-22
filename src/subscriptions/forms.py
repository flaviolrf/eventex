# coding: utf-8

from django import forms
from .models import Subscription 
from django.contrib.localflavor.br.forms import BRCPFField, BRPhoneNumberField
from django.utils.translation import ungettext, ugettext as _



class SubscriptionForm(forms.ModelForm):
	class Meta:
		model = Subscription
		exclude = ('paid',)
	cpf = BRCPFField(max_length=11)
	phone = BRPhoneNumberField(required=False)

	def clean(self):
		super(SubscriptionForm, self).clean()

		if not self.cleaned_data.get('email') and not self.cleaned_data.get('phone'):
			raise forms.ValidationError(_(u'Informe email ou telefone'))
		return self. cleaned_data

