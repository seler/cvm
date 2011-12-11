from __future__ import absolute_import

from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from .forms import ProfileForm
from .models import Profile


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

# requires review
@login_required
def change_passwd(request):
    try: # does this need handling anyway?
        profile = Profile.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return redirect() # where to?
    form = PasswordChangeForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('user_profile', request.user.username)
    return render(request, "accounts/change_password.html", {"form" : form})
