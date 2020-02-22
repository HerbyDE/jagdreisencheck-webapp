import jwt
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from accounts.models import User

reg_key = settings.REG_KEY


def generate_password_reset_token(request, user=None):
    user = user
    key = reg_key

    try:
        user = User.objects.get(email=user.email)
        num_of_request = 1

        if user.has_password_reset_token():
            # old_token = jwt.decode(token=user.reset_token, key=key, algorithms=['HS256'], verify=True)
            # num_of_request = old_token.get('num_of_requests')
            num_of_request += 1

            if num_of_request > 4:
                return u'%s' % _('You have exceeded the max. number of resets. Please contact us!')

        else:
            num_of_request = 1

        token_content = {
            'user': user.email,
            'iat': timezone.now(),
            'exp': timezone.now() + timezone.timedelta(days=2),
            'num_of_requests': num_of_request
        }

        token = jwt.encode(payload=token_content, key=key, algorithm='HS256')

        result = {
            'status': 1,
            'token': token
        }

        return result

    except User.DoesNotExist or TypeError or AttributeError:
        messages.error(request=request, message=_('We could not find this user!'))
        raise ValueError(_('A user with these credentials does not exist!'))


def decode_password_reset_token(request, token):
    key = reg_key

    try:
        token_content = jwt.decode(token=token, key=key, algorithms=['HS256'], verify=True)

        if token_content['num_of_requests'] < 5:
            try:
                user = User.objects.get(email=token_content['user'])
                return user

            except User.DoesNotExist:
                messages.error(request=request, message=_('Your token is invalid!'))
                return False

    except jwt.ExpiredSignatureError:
        messages.error(request=request, message=_('Your token has expired!'))
        return False


def verify_activation_token(token=None):
    try:
        token_content = jwt.decode(token=token, key=reg_key, algorithms=['HS256'], verify=True)

        user = token_content.get('user')

        '''
        The verification returns a user e-mail but the issue date could also be retrived. No further information is 
        stored.
        '''

        return user

    except jwt.ExpiredSignatureError:
        return False