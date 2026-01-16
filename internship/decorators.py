from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from functools import wraps

def role_required(roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if hasattr(request.user, 'profile'):
                if request.user.profile.role in roles:
                    return view_func(request, *args, **kwargs)
            return redirect('login')
        return _wrapped_view
    return decorator

