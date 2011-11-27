from __future__ import absolute_import
from django import forms

from sharing.models import Share
from resumes.models import Resume, Identity

class IdentityForm(forms.ModelForm):
    class Meta(object):
        model = Identity
        exclude = ('user',)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(IdentityForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(IdentityForm, self).save(commit=False)
        instance.user = self.request.user
        if commit:
            instance.save()
        return instance

class ShareForm(forms.ModelForm):

    class Meta(object):
        model = Share

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ShareForm, self).__init__(*args, **kwargs)
        choices = Resume.objects.filter(identity__user=self.request.user).values_list('id', 'name')
        self.fields["resume"].choices = choices
