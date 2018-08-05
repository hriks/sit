from __future__ import absolute_import, unicode_literals

from sit import settings

from rest_framework.response import Response

ERROR_CODES = {
    "INVN000": "Internal Server Error.",
    "INVN001": "Access token not provided.",
    "INVN002": "Invalid accesstoken provided.",
    "INVN003": "User doesnot exists.",
    "INVN004": "Incorrect fields provided.",
    "INVN005": "Mandatory fields are missing.",
    "INVN006": "User already exists with this username.",
    "INVN007": "Assignee not found with the username provided. Please verify username",
    "INVN008": "Issue is not created by requesting user",
    "INVN009": "Issue could not be raised as similar issue was found."
}


class InvalidAccessToken(Exception):
    pass


class IssueAlreadyRegistered(Exception):
    pass


def make_exc_response(
        data, error_code, status_code, excpetion=None, reason=""):
    response = {
        "success": False,
        "error_code": error_code,
        "error_message": (
            str(excpetion) if settings.DEBUG and status_code == 500 and excpetion else ERROR_CODES[error_code] + " " + reason  # noqa
        ),
        "status_code": status_code
    }
    return Response(response, status=status_code)


def make_success_response(data, response, status):
    response.update({
        "success_message": "Request processed successfully!",
        "status_code": status
    })
    return Response(response, status=status)


def auth_required():
    def wrap(view):
        def wrapper(request, *args, **kwargs):
            try:
                if request.method == 'GET':
                    data = request.GET.dict()
                else:
                    data = request.POST.dict()
                from .models import User
                user = User.decodeAccessToken(data['accesstoken'])
            except KeyError:
                return make_exc_response(data, "INVN001", 403)
            except InvalidAccessToken:
                return make_exc_response(data, "INVN002", 428)
            except User.DoesNotExist:
                return make_exc_response(data, "INVN003", 403)
            except Exception as e:
                return make_exc_response(data, "INVN000", 500, e)
            return view(request, user, *args, **kwargs)
        return wrapper
    return wrap
