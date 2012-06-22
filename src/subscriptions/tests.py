# coding: utf-8

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse
from .models import Subscription
from django.db import IntegrityError
from .forms import SubscriptionForm
from django.core import mail
from django.conf import settings
from mock import Mock
from .models import Subscription
from .admin import SubscriptionAdmin, Subscription, admin
from django.contrib.auth.models import User
from django.utils.translation import ungettext, ugettext as _


class SubscriptionUrlTest(TestCase):
	def test_get_subscribe_page(self):
		'Veririfca se existe rota para formulário de incrição'
		response = self.client.get(reverse('subscriptions:subscribe'))
		self.assertEquals(200, response.status_code)

	#def test_get_success_page(self):
	#	'Verifica se existe rota para página de sucesso'
	#	response = self.client.get(reverse('subscriptions:success', args=[1]))
	#	self.assertEquals(200, response.status_code)

class SubscribeViewTest(TestCase):
	def setUp(self):
		self.resp = self.client.get(reverse('subscriptions:subscribe'))

	def test_get(self):
		'Ao visitar /inscicao/ a página de inscrição é exibida'
		self.assertEquals(200, self.resp.status_code)

	def test_use_template(self):
		'O corpo da resposta deve conter um template'
		self.assertTemplateUsed(self.resp, 'subscriptions/subscription_form.html')

	def test_has_form(self):
		'A resposta deve conter o formulário de inscrição'
		self.assertIsInstance(self.resp.context['form'], SubscriptionForm)

	def test_form_has_fields(self):
		'O formulário deve conter name, email, cpf, e phone'
		form = self.resp.context['form']
		self.assertItemsEqual(['name', 'email', 'cpf', 'phone'], form.fields)

	def test_html(self):
		'O html deve conter os campos do formulário'
		self.assertContains(self.resp, '<form')
		self.assertContains(self.resp, '<input', 6)
		self.assertContains(self.resp, 'type="text"', 4)
		self.assertContains(self.resp, 'type="submit"')

class SuccessViewTest(TestCase):
	def setUp(self):
		s = Subscription.objects.create(
			name='Flávio França',
			cpf='79129250404',
			email='flaviolrf@gmail.com',
			phone='84-91520741'
		)
		self.resp = self.client.get(reverse('subscriptions:success', args=[s.pk]))

	def test_get(self):
		'Visita /inscicao/1/ e retorna 200'
		self.assertEquals(200, self.resp.status_code)

	def test_template(self):
		'Renderiza o template'
		self.assertTemplateUsed(self.resp, 'subscriptions/subscription_detail.html')

	def test_context(self):
		'Verifica instância de subscription no contexto'
		subscription = self.resp.context['subscription']
		self.assertIsInstance(subscription, Subscription)

	def test_html(self):
		'Pagina deve conter nome do cadastrado'
		self.assertContains(self.resp, 'Flávio França')

class SuccessViewNotFound(TestCase):
	def test_not_found(self):
		'Acesso à instancia não cadastrada deve retornar 404'
		response = self.client.get(reverse('subscriptions:success', args=[0]))
		self.assertEqual(404, response.status_code)


class SubscribeViewPostTest(TestCase):
    def setUp(self):
        data = dict(name='Henrique Bastos', cpf='00000000000',
                    email='henrique@bastos.net', phone='21-96186180')
        self.resp = self.client.post(reverse('subscriptions:subscribe'), data)

    def test_post(self):
        "Post deve redirecionar para página de sucesso."
        self.assertRedirects(self.resp,
                             reverse('subscriptions:success', args=[1]))

    def test_save(self):
        "Post deve salvar Subscription no banco."
        self.assertTrue(Subscription.objects.exists())

    def test_email_sent(self):
    	'Post deve notificar visitante por email.'
    	self.assertEquals(1, len(mail.outbox))

class SubscribeViewInvalidPostTest(TestCase):
    def setUp(self):
        data = dict(name='Flávio França', cpf='000000000000001',
                    email='henrique@bastos.net', phone='21-96186180')
        self.resp = self.client.post(reverse('subscriptions:subscribe'), data)
    
    def test_show_page(self):
        "Post inválido não deve redirecionar."
        self.assertEqual(200, self.resp.status_code)

    def test_form_errors(self):
        "Form deve conter erros."
        self.assertTrue(self.resp.context['form'].errors)

    def test_must_not_save(self):
        "Dados não devem ser salvos."
        self.assertFalse(Subscription.objects.exists())

class SubscriptionModelTest(TestCase):
	def test_create(self):
		'O model deve ter name, cpf, email, phone, created_at'
		s = Subscription.objects.create(
			name='Flávio França',
			cpf='79129250404',
			email='flaviolrf@gmail.com',
			phone='84-91520741'
		)
		self.assertEquals(s.id, 1)

class SubscriptionModelUniqueTest(TestCase):
	def setUp(self):
		# Cria uma 1ª inscrição no banco
		Subscription.objects.create(name='Flávio França', cpf='79129250404',
									email='flaviolrf@gmail.com', phone='84-91520741')

	def test_cpf_must_be_unique(self):
		'CFP deve ser único'
		# Instancia a inscrição com CPF existente
		s = Subscription(name='Flávio França', cpf='79129250404',
						email='outro@email.com', phone='84-91520741')
		# Verifica se ocorre o erro de integridade ao persistir
		self.assertRaises(IntegrityError, s.save)

	#def test_email_must_be_unique(self):
	#	'Email deve ser único'
	#	# Instancia a inscrição com email existente
	#	s = Subscription(name='Flávio França', cpf='00000000000',
	#					email='flaviolrf@gmail.com', phone='84-91520741')
		# Verifica se ocorre o erro de integridade ao persistir
	#	self.assertRaises(IntegrityError, s.save)

class CustomActionTest(TestCase):
	def setUp(self):
		Subscription.objects.create(
			name='Flávio França',
			cpf='79129250404',
			email='flaviolrf@gmail.com',
			phone='84-91520741'
			)
		self.modeladmin = SubscriptionAdmin(Subscription, admin.site)
		self.modeladmin.mark_as_paid(Mock(), Subscription.objects.all())

	def test_update_paid(self):
		'Dados devem ser atualizados como pagos de acordo com o Queryset'
		self.assertEqual(1, Subscription.objects.filter(paid=True).count())

	#def test_update_unpaid(self):
	#	'Dados devem ser atualizados como não pagos de acordo com o Queryset'
	#	self.assertEqual(1, Subscription.objects.filter(paid=False).count())

class ExportSubscriptionViewTest(TestCase):
	def setUp(self):
		User.objects.create_superuser('admin', 'admin@admin.com', 'admin')
		assert self.client.login(username='admin', password='admin')
		self.resp = self.client.get(reverse('admin:export_subscriptions'))

	def test_get(self):
		u'Sucesso ao acessar url de download do arquivo csv'
		self.assertEqual(200, self.resp.status_code)

	def test_content_type(self):
		u'Content type deve ser text/csv'
		self.assertEqual('text/csv', self.resp['Content-Type'])

	def test_attachment(self):
		u'Header indicando ao browser que a resposta é um arquivo a ser salvo'
		self.assertTrue('attachment;' in self.resp['Content-Disposition'])

class ExportSubscriptionsNotFound(TestCase):
	def test_404(self):
		u'Login é exigido para download do csv'
		# Quando o usuário não está autenticado
		# o admin responde 200 e renderiza o html de login
		response = self.client.get(reverse('admin:export_subscriptions'))
		self.assertTemplateUsed(response, 'admin/login.html')

class SubscritpionFormTest(TestCase):
    def test_must_inform_email_or_phone(self):
        u'Email e Phone são opcionais, mas ao menos 1 precisa ser informado.'
        form = self.make_and_validate_form(email='', phone='')
        self.assertDictEqual(form.errors,
                             {'__all__': [u'Informe seu e-mail ou telefone.']})

    def make_and_validate_form(self, **kwargs):
        data = dict(name='Flávio França', email='flaviolrf@gmail.com', cpf='00000000000', phone='84-91520741')
        data.update(kwargs)
        form = SubscriptionForm(data)
        form.is_valid()
        return form
