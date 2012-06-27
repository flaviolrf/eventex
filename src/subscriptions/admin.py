# coding: utf-8

from django.utils.datetime_safe import datetime
from django.contrib import admin
from .models import Subscription
from django.utils.translation import ungettext, ugettext as _
from django.conf.urls import patterns, url
from django.http import HttpResponse

class SubscriptionAdmin(admin.ModelAdmin):
	list_display = ('name', 'email', 'phone', 'created_at', 'subscribed_today', 'paid')
	date_hierarchy = 'created_at'
	search_fields = ('name', 'cpf', 'email', 'phone', 'created_at')
	list_filter = ['created_at', 'paid']
	actions = ['mark_as_paid', 'mark_as_unpaid']

	def subscribed_today(self, obj):
		return obj.created_at.date() == datetime.today().date()
	subscribed_today.short_description = u'Inscrito hoje?'
	subscribed_today.boolean = True

	def mark_as_paid(self, request, queryset):
		count = queryset.update(paid=True)

		msg = ungettext(
			u'%(count)d inscrição foi marcada como paga.',
			u'%(count)d inscrições foram marcadas como pagas.',
			count
		) % {'count': count}
		self.message_user(request, msg)
	mark_as_paid.short_description = _(u'Marcar como pagas')

	def mark_as_unpaid(self, request, queryset):
		count = queryset.update(paid=False)

		msg = ungettext(
			u'%(count)d inscrição foi marcada como não paga.',
			u'%(count)d inscrições foram marcadas como não pagas.',
			count
		) % {'count': count}
		self.message_user(request, msg)
	mark_as_unpaid.short_description = _(u'Marcar como não pagas')

	def get_urls(self):
		original_urls = super(SubscriptionAdmin, self).get_urls()
		extra_url = patterns('',
							# Envolvendo a view em 'admin_view' porque ela faz o 
							#controle de permissões e cache automaticamente
							url(r'exportar-inscricoes/$', self.admin_site.admin_view(self.export_subscriptions),
							name='export_subscriptions')
							)

	# Aordem é importante. As urls originais do admin são muito permissivas
	# e acabam sendo encontradas antes
		return extra_url + original_urls

	def export_subscriptions(self, request):
		subscriptions = self.model.objects.all()
		rows = [','.join([s.name, s.email, s.phone]) for s in subscriptions]
		response = HttpResponse('\r\n'.join(rows), content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename=inscricoes.csv'

		return response

admin.site.register(Subscription, SubscriptionAdmin)