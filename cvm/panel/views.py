from __future__ import absolute_import

import hashlib

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.forms.models import inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.utils.functional import lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import UpdateView, CreateView, DeleteView

from resumes.models import *
from sharing.models import Share

from .forms import (IdentityForm, ShareForm, IdentityFieldFormSet,
                    ResumeForm, SectionForm)
from django.views.generic.list_detail import object_detail

reverse_lazy = lambda name = None, *args: lazy(reverse, str)(name, args=args)


class MyCreateView(CreateView):
    """Abstract. Slightly extended standard `CreateView`."""
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
        kwargs.update({'request': self.request})
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
    """Abstract. Slightly extended `UpdateView`."""
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
        message = _("Successfully updated %s \"%s\".") % \
                  (self.object_name, self.object)
        messages.success(self.request, message)
        return super(MyUpdateView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(MyUpdateView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MyUpdateView, self).dispatch(*args, **kwargs)


class MyDeleteView(DeleteView):
    """Abstract. Slightly extended `DeleteView`."""
    object_name = None
    success_url = reverse_lazy('panel_home')

    def get_template_names(self):
        return ['panel/confirm_delete.html']

    def get_context_data(self, **kwargs):
        context = super(MyDeleteView, self).get_context_data(**kwargs)
        context['object_name'] = self.object_name
        return context

    def post(self, *args, **kwargs):
        message = _("Successfully deleted %s \"%s\".") % \
                  (self.object_name, self.get_object())
        messages.success(self.request, message)
        return super(MyDeleteView, self).post(*args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MyDeleteView, self).dispatch(*args, **kwargs)


@login_required
def home(request):
    """Renders homepage."""
    context_vars = {
        'identity_list': Identity.objects.filter(user=request.user),
        'resume_list': Resume.objects.filter(identity__user=request.user),
        'share_list': Share.objects.filter(resume__identity__user=request.user)
    }
    return render_to_response('panel/home.html', context_vars,
        context_instance=RequestContext(request))


class IdentityCreateView(MyCreateView):
    """Widok tworzenia nowego `Identity`."""
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
    """Widok zmiany `Identity`."""
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
            context['identity_field_formset'] = IdentityFieldFormSet(queryset=IdentityField.objects.all())
        return context


class IdentityDeleteView(MyDeleteView):
    """Widok usuwane `Identity`."""
    model = Identity
    object_name = 'identity'

    def get_queryset(self):
        self.queryset = Identity.objects.filter(user=self.request.user)
        return self.queryset._clone()


class ShareCreateView(MyCreateView):
    """Widok tworzenia nowego wspoludzialu."""
    model = Share
    form_class = ShareForm
    object_name = 'share'

    def get_initial(self):
        self.initial.update({'resume': self.kwargs.get('resume_pk', None)})
        return self.initial


class ShareUpdateView(MyUpdateView):
    """Widok edycji wspoludzialu."""
    form_class = ShareForm
    object_name = 'share'

    def get_queryset(self):
        self.queryset = Share.objects.filter(resume__identity__user=self.request.user)
        return self.queryset._clone()


class ShareDeleteView(MyDeleteView):
    """Widok usuwania wspoludzialu."""
    model = Share
    object_name = 'share'

    def get_queryset(self):
        self.queryset = Share.objects.filter(resume__identity__user=self.request.user)
        return self.queryset._clone()


class ResumeDeleteView(MyDeleteView):
    """Widok usuwania `Resume`."""
    model = Resume
    object_name = 'resume'

    def get_queryset(self):
        self.queryset = Resume.objects.filter(identity__user=self.request.user)
        return self.queryset._clone()


@login_required
def resume_detail(request, object_id):
    """Widok podgladu szczegolow `Resume`."""
    queryset = Resume.objects.filter(identity__user=request.user)
    return object_detail(request, queryset,
        object_id=object_id,
        template_name='panel/resume_detail.html'
    )


@login_required
def resume_edit(request, object_id=None):
    """Widok tworzenia i edycji `Resume`."""
    SectionFormSet = inlineformset_factory(Resume, Section, extra=0)
    context_vars = {
        'object_name': _('resume')
    }
    if object_id:
        obj = get_object_or_404(Resume, id=object_id)
        context_vars['object'] = obj
    if request.method == 'POST':
        if object_id:
            section_formset = SectionFormSet(request.POST, instance=obj,
                prefix='section')
            form = ResumeForm(request.POST, request.FILES, request=request,
                instance=obj)
            if form.is_valid() and section_formset.is_valid():
                instance = form.save()
                section_formset.save()
                message = _("Successfully saved resume \"%s\".") % instance
                messages.success(request, message)
                return HttpResponseRedirect(reverse_lazy('panel_home'))

        else:
            form = ResumeForm(request.POST, request.FILES, request=request)
            if form.is_valid():
                instance = form.save()
                message = _("Successfully saved resume \"%s\".") % instance
                messages.success(request, message)
                return HttpResponseRedirect(reverse_lazy('panel_home'))
    else:
        if object_id:
            section_formset = SectionFormSet(instance=obj, prefix='section')
            form = ResumeForm(instance=obj, request=request)
        else:
            #section_formset = SectionFormSet(prefix='section')
            form = ResumeForm(request=request)

    context_vars['form'] = form
    if object_id:
        context_vars['section_formset'] = section_formset
    return render_to_response('panel/resume_form.html', context_vars,
        RequestContext(request))


@login_required
def section_edit(request, resume_id, section_id):
    """Widok tworzenia i edcji sekcji."""
    SectionEntryFormSet = inlineformset_factory(Section, SectionEntry, extra=0)
    obj = get_object_or_404(Section, id=section_id, resume__id=resume_id)
    if request.method == 'POST':
        section_entry_formset = SectionEntryFormSet(request.POST, instance=obj,
            prefix='section_entry')
        form = SectionForm(request.POST, request.FILES, request=request,
            instance=obj)
        if form.is_valid() and section_entry_formset.is_valid():
            instance = form.save()
            section_entry_formset.save()
            message = _("Successfully saved resume \"%s\".") % (instance)
            messages.success(request, message)
            return HttpResponseRedirect(reverse_lazy('panel_home'))
    else:
        section_entry_formset = SectionEntryFormSet(instance=obj,
            prefix='section_entry')
        form = SectionForm(instance=obj, request=request)

    context_vars = {
        'form': form,
        'object_name': _('section')
    }
    context_vars['object'] = obj
    context_vars['section_entry_formset'] = section_entry_formset
    return render_to_response('panel/section_form.html', context_vars,
        RequestContext(request))
