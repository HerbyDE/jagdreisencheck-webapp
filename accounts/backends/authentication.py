from django.contrib.auth import get_user_model  # gets the user_model django  default or your own custom
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from accounts.models import IndividualProfile, CorporateProfile


# Class to permit the athentication using email or username
class EmailUsernameAuthBackend(ModelBackend):  # requires to define two functions authenticate and get_user

    def authenticate(self, username=None, password=None, **kwargs):
        user = get_user_model()

        try:
            # below line gives query set,you can change the queryset as per your requirement
            user = user.objects.filter(
                Q(username__iexact=username) |
                Q(email__iexact=username)
            ).distinct()

        except user.DoesNotExist:
            return None

        if user.exists():
            ''' get the user object from the underlying query set,
            there will only be one object since username and email
            should be unique fields in your models.'''
            user_obj = user.first()
            if user_obj.check_password(password):
                try:
                    individual = IndividualProfile.objects.get(user=user_obj)
                    return individual
                except IndividualProfile.DoesNotExist:
                    try:
                        corporate = CorporateProfile.objects.get(user=user_obj)
                        return corporate
                    except CorporateProfile.DoesNotExist:
                        return user_obj

            return None

        return None

    def get_user(self, user_id):

        user = get_user_model()
        try:
            user.objects.get(pk=user_id)
        except user.DoesNotExist:
            return None

        return user if self.user_can_authenticate(user) else None
