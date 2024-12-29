from django.shortcuts import redirect
from django.contrib import messages

def email_verified_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.email_verified:
            messages.warning(request, "Vui lòng xác nhận email để sử dụng tính năng này.")
            return redirect("profile-settings")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
