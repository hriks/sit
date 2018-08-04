from sit import settings

from django.http import JsonResponse
from apis.models import User

ERROR_CODES = {
    "INVN000": "Internal Server Error",
    "INVN001": "Access token not provided.",
    "INVN002": "Invalid accesstoken provided",
    "INVN003": "User doesnot exists",
    "INVN004": "",
    "INVN005": "",
    "INVN006": "",
    "INVN007": "",  # noqa
    "INVN008": "",
    "INVN009": ""
}


class InvalidAccessToken(Exception):
    pass


def make_exc_response(
        data, error_code, status_code, excpetion=None, reason=""):
    response = {
        "success": False,
        "error_code": error_code,
        "error_message": (
            str(excpetion) if settings.DEBUG and status_code == 500 and excpetion else ERROR_CODES[error_code] + reason  # noqa
        ),
        "status_code": status_code
    }
    return JsonResponse(response, status=status_code)


def make_success_response(data, response, status):
    response.update({
        "success_message": "Request processed successfully!",
        "status_code": status
    })
    return JsonResponse(response, status=status)


def auth_required(f, methods={
        "GET": 0, "POST": 0, "PUT": 0, "DELETE": 0}):
    def wrap(request, *args, **kwargs):
        try:
            if request.method == 'GET':
                data = request.GET.dict()
            else:
                data = request.POST.dict()
            user = User.decodeAccessToken(data['accessToken'])
        except KeyError:
            return make_exc_response(data, "INVN001", 403)
        except InvalidAccessToken:
            return make_exc_response(data, "INVN002", 428)
        except User.DoesNotExist:
            return make_exc_response(data, "INVN003", 403)
        except Exception as e:
            return make_exc_response(data, "INVN000", 500, e)
        return f(request, user, *args, **kwargs)
    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap
