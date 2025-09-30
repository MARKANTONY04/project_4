#logged in users can change/update name

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm

@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile_updated')  
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'accounts/update_profile.html', {'form': form})
