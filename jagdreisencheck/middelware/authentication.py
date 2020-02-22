from django.shortcuts import HttpResponseRedirect, reverse
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from re import compile


class RequireLoginMiddleware(MiddlewareMixin):

    def process_request(self, request):

        if not request.user.is_authenticated:
            path = "{}".format(request.path)
            login_url = "/{}{}".format(request.LANGUAGE_CODE, settings.LOGIN_URL)
            robots_url = "/{}".format('robots.txt')

            if not path or not any(path == eu for eu in [login_url, robots_url]):
                print("Logged out: ", any(path == eu for eu in [login_url, robots_url]))
                return HttpResponseRedirect(login_url)