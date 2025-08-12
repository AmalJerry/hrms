from django.http import HttpResponse
from django.shortcuts import redirect

# def allowed_users(allowed_roles=[]):
#     def decorator(view_func):
#         def wrapper_func(request, *args, **kwargs):
#             role=None
#             print(request.user.role)
#             if request.user.role in allowed_roles:
#                 return view_func(request, *args, **kwargs)
#             else:
#                 return HttpResponse("You are not authorized to view this page")
#         return wrapper_func
#     return decorator


def allowed_users(allowed_roles=[], allowed_statuses=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if (
                request.user.role in allowed_roles
                and request.user.status in allowed_statuses
            ):
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse("You are not authorized to view this page")

        return wrapper_func

    return decorator

