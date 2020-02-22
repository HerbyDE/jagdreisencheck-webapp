import os


def testsystem(request):

    return {'is_testsystem': eval(os.environ.get('testsystem', "True"))}