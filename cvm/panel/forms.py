from __future__ import absolute_import
from django import forms

from sharing.models import Share
from resumes.models import Resume, Identity, IdentityField, Section

class IdentityForm(forms.ModelForm):
    """Formularz tworzenia i edycji `Identity`."""
    class Meta(object):
        model = Identity
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(IdentityForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(IdentityForm, self).save(commit=False)
        try:
            instance.user = self.request.user
        except AttributeError:
            # formsets
            pass
        if commit:
            instance.save()
        return instance

class ShareForm(forms.ModelForm):
    """Formularz tworzenia i edycji `Share`."""

    class Meta(object):
        model = Share

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ShareForm, self).__init__(*args, **kwargs)
        choices = Resume.objects.filter(identity__user=self.request.user).values_list('id', 'name')
        self.fields["resume"].choices = choices


IdentityFieldFormSet = forms.models.inlineformset_factory(Identity, IdentityField, form=IdentityForm, extra=3, can_order=True, can_delete=True)

class ResumeForm(forms.ModelForm):
    """Formularz tworzenia i edycji `Resume`."""

    class Meta(object):
        model = Resume

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ResumeForm, self).__init__(*args, **kwargs)
        choices = Identity.objects.filter(user=self.request.user).values_list('id', 'name')
        self.fields["identity"].choices = choices


class SectionForm(forms.ModelForm):
    """Formularz tworzenia i edycji `Section`."""

    class Meta(object):
        model = Section

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(SectionForm, self).__init__(*args, **kwargs)
        choices = Resume.objects.filter(identity__user=self.request.user).values_list('id', 'name')
        self.fields["resume"].choices = choices
