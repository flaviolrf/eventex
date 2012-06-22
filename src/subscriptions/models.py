# coding: utf-8

from django.db import models


class Subscription(models.Model):
	name = models.CharField(u'Nome', max_length=100)
	cpf = models.CharField(u'CPF', max_length=11, unique=True)
	email = models.EmailField(u'E-mail', blank=True)
	phone = models.CharField(u'Telefone' ,max_length=12, blank=True)
	created_at = models.DateTimeField(u'Criado em', auto_now_add=True)
	paid = models.BooleanField(u'Pago?')

	def __unicode__(self):
		return self.name