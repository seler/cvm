from __future__ import absolute_import

import hashlib
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import DetailView, ListView
from .forms import ProfileForm
from .models import Profile, Identity


def user_profile(request, username):
    u = get_object_or_404(User, username=username)
    ctx = {
        'object': u,
    }
    return render(request, "accounts/user_profile.html", ctx)

@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, instance=profile)
    if form.is_valid():
        form.save()
        return redirect('user_profile', request.user.username)
    return render(request, "accounts/edit_profile.html", {'form': form})


class ResumeDetailView(DetailView):
    def get_queryset(self):
        self.queryset = Resume.objects.qs_for_view(self.request, self.kwargs.get('username'), self.kwargs.get('slug'))
        return self.queryset._clone()

    def get_template_names(self):
        return [self.object.get_template_name()]

class IdentityListView(ListView):
    def get_queryset(self):
        self.queryset = Identity.objects.filter(user=self.request.user)
        return self.queryset._clone()
