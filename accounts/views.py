#logged in users can change/update name

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .forms import UpdateProfileForm

@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            # Stay on the same page, just re-render with success message
    else:
        form = UpdateProfileForm(instance=request.user)

    return render(request, 'accounts/update_profile.html', {'form': form})
