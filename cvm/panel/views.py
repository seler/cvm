from __future__ import absolute_import

import hashlib
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import DetailView, ListView, UpdateView, CreateView
from accounts.models import Identity
from django.template import RequestContext
from cvm1.models import Resume
from sharing.models import Share
from .forms import IdentityForm, ShareForm
from django.core.urlresolvers import reverse
from django.utils.functional import lazy

reverse_lazy = lambda name = None, *args : lazy(reverse, str)(name, args=args)

@login_required
def home(request):
    context_vars = {
        'identity_list': Identity.objects.filter(user=request.user),
        'resume_list': Resume.objects.filter(identity__user=request.user),
        'share_list': Share.objects.filter(resume__identity__user=request.user),
    }
    return render_to_response('panel/home.html', context_vars, context_instance=RequestContext(request))

class IdentityCreateView(CreateView):
    model = Identity
    form_class = IdentityForm
    success_url = reverse_lazy('panel_home')

    def get_template_names(self):
        return ['panel/identity_form.html']

    def get_form_kwargs(self):
        kwargs = super(IdentityCreateView, self).get_form_kwargs()
        kwargs.update({'request':self.request})
        return kwargs

class IdentityUpdateView(UpdateView):
    form_class = IdentityForm
    success_url = reverse_lazy('panel_home')

    def get_queryset(self):
        self.queryset = Identity.objects.filter(user=self.request.user)
        return self.queryset._clone()

    def get_template_names(self):
        return ['panel/identity_form.html']


class ShareCreateView(CreateView):
    model = Share
    form_class = ShareForm
    success_url = reverse_lazy('panel_home')

    def get_template_names(self):
        return ['panel/share_form.html']

    def get_form_kwargs(self):
        kwargs = super(ShareCreateView, self).get_form_kwargs()
        kwargs.update({'request':self.request})
        return kwargs

    def get_initial(self):
        self.initial.update({'resume': self.kwargs.get('resume_pk', None)})
        return self.initial

class ShareUpdateView(UpdateView):
    form_class = ShareForm
    success_url = reverse_lazy('panel_home')

    def get_queryset(self):
        self.queryset = Share.objects.filter(resume__identity__user=self.request.user)
        return self.queryset._clone()

    def get_template_names(self):
        return ['panel/share_form.html']

    def get_form_kwargs(self):
        kwargs = super(ShareUpdateView, self).get_form_kwargs()
        kwargs.update({'request':self.request})
        return kwargs
