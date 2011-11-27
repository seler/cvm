from __future__ import absolute_import

import hashlib
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.views.generic import DetailView, ListView, UpdateView, CreateView, DeleteView
from django.template import RequestContext
from resumes.models import Resume, Identity
from sharing.models import Share
from .forms import IdentityForm, ShareForm, IdentityFieldFormSet
from django.core.urlresolvers import reverse
from django.utils.functional import lazy
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

reverse_lazy = lambda name = None, *args : lazy(reverse, str)(name, args=args)


class MyCreateView(CreateView):
    object_name = None
    success_url = reverse_lazy('panel_home')
    template_name = 'panel/form.html'

    def get_template_names(self):
        if self.template_name:
            return [self.template_name]
        else:
            return super(MyCreateView, self).get_template_names()

    def get_form_kwargs(self):
        kwargs = super(MyCreateView, self).get_form_kwargs()
        kwargs.update({'request':self.request})
        return kwargs

    def form_valid(self, form):
        message = _("Successfully created new %s.") % self.object_name
        messages.success(self.request, message)
        return super(MyCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(MyCreateView, self).get_context_data(**kwargs)
        context['object_name'] = self.object_name
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MyCreateView, self).dispatch(*args, **kwargs)


class MyUpdateView(UpdateView):
    object_name = None
    success_url = reverse_lazy('panel_home')
    template_name = 'panel/form.html'

    def get_template_names(self):
        if self.template_name:
            return [self.template_name]
        else:
            return super(MyUpdateView, self).get_template_names()

    def get_context_data(self, **kwargs):
        context = super(MyUpdateView, self).get_context_data(**kwargs)
        context['object_name'] = self.object_name
        return context

    def form_valid(self, form):
        message = _("Successfully updated %s \"%s\".") % (self.object_name, self.object)
        messages.success(self.request, message)
        return super(MyUpdateView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(MyUpdateView, self).get_form_kwargs()
        kwargs.update({'request':self.request})
        return kwargs

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MyUpdateView, self).dispatch(*args, **kwargs)

class MyDeleteView(DeleteView):
    object_name = None
    success_url = reverse_lazy('panel_home')

    def get_template_names(self):
        return ['panel/confirm_delete.html']

    def get_context_data(self, **kwargs):
        context = super(MyDeleteView, self).get_context_data(**kwargs)
        context['object_name'] = self.object_name
        return context

    def post(self, *args, **kwargs):
        message = _("Successfully deleted %s \"%s\".") % (self.object_name, self.get_object())
        messages.success(self.request, message)
        return super(MyDeleteView, self).post(*args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MyDeleteView, self).dispatch(*args, **kwargs)


@login_required
def home(request):
    context_vars = {
        'identity_list': Identity.objects.filter(user=request.user),
        'resume_list': Resume.objects.filter(identity__user=request.user),
        'share_list': Share.objects.filter(resume__identity__user=request.user),
    }
    return render_to_response('panel/home.html', context_vars, context_instance=RequestContext(request))


class IdentityCreateView(MyCreateView):
    object_name = 'identity'
    model = Identity
    form_class = IdentityForm
    template_name = 'panel/identity_form.html'

    def form_valid(self, form):
        context = self.get_context_data()
        identity_field_formset = context['identity_field_formset']
        if identity_field_formset.is_valid():
            self.object = form.save()
            identity_field_formset.instance = self.object
            identity_field_formset.save()
            return super(IdentityCreateView, self).form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(IdentityCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['identity_field_formset'] = IdentityFieldFormSet(self.request.POST)
        else:
            context['identity_field_formset'] = IdentityFieldFormSet()
        return context


class IdentityUpdateView(MyUpdateView):
    form_class = IdentityForm
    object_name = 'identity'
    template_name = 'panel/identity_form.html'

    def get_queryset(self):
        self.queryset = Identity.objects.filter(user=self.request.user)
        return self.queryset._clone()

    def form_valid(self, form):
        context = self.get_context_data()
        identity_field_formset = context['identity_field_formset']
        if identity_field_formset.is_valid():
            self.object = form.save()
            identity_field_formset.instance = self.object
            identity_field_formset.save()
            return super(IdentityUpdateView, self).form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(IdentityUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['identity_field_formset'] = IdentityFieldFormSet(self.request.POST)
        else:
            context['identity_field_formset'] = IdentityFieldFormSet()
        return context


class IdentityDeleteView(MyDeleteView):
    model = Identity
    object_name = 'identity'

    def get_queryset(self):
        self.queryset = Identity.objects.filter(user=self.request.user)
        return self.queryset._clone()


class ShareCreateView(MyCreateView):
    model = Share
    form_class = ShareForm
    object_name = 'share'

    def get_initial(self):
        self.initial.update({'resume': self.kwargs.get('resume_pk', None)})
        return self.initial


class ShareUpdateView(MyUpdateView):
    form_class = ShareForm
    object_name = 'share'

    def get_queryset(self):
        self.queryset = Share.objects.filter(resume__identity__user=self.request.user)
        return self.queryset._clone()




class ShareDeleteView(MyDeleteView):
    model = Share
    object_name = 'share'

    def get_queryset(self):
        self.queryset = Share.objects.filter(resume__identity__user=self.request.user)
        return self.queryset._clone()
