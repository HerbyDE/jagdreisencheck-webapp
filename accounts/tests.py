from django.contrib.auth.hashers import check_password
from django.test import TestCase

from accounts.forms import CreateBaseUserInstance
from accounts.models import User


# Unit tests for SignUp and Registration
class UserManagementTestCase(TestCase):

    def test_create_base_user_form(self):
        '''
        Test form behavior. Failure and Validation.
        This method checks whether the
        :return:
        '''
        invalid_base_data = {
            'email': 'max.mustermann@jagdreisencheck.de',
            'username': 'maxmustermann',
            'password': 'testword123',
            'confirm_passwd': 'testwort123',
            'first_name': 'Max',
            'last_name': 'Mustermann',
            'country_of_residence': 'DE',
            'agree_to_privacy': True,
            'agree_to_tos': True
        }

        valid_base_data = {
            'email': 'max.mustermann@jagdreisencheck.de',
            'username': 'maxmustermann',
            'password': 'testword123',
            'confirm_passwd': 'testword123',
            'first_name': 'Max',
            'last_name': 'Mustermann',
            'country_of_residence': 'DE',
            'agree_to_privacy': True,
            'agree_to_tos': True
        }

        # Test form with invalid data
        form = CreateBaseUserInstance(data=invalid_base_data)
        form.is_valid()
        self.assertTrue(form.errors)

        # Test form with valid data and write it to the database. Then retrieve the base user instance and compare it to
        # the submitted form.
        form = CreateBaseUserInstance(data=valid_base_data)
        form.is_valid()
        self.assertFalse(form.errors)
        form = form.save(commit=False)
        self.assertTrue(isinstance(form, User))
        form.save()
        maxi = User.objects.get(email='max.mustermann@jagdreisencheck.de')
        self.assertEqual(maxi, form, msg="User found in DB.")
        self.assertTrue(check_password(valid_base_data['password'], maxi.password))

    def test_create_individual_user(self):
        '''
        Test the individual user creation procedure. Uses the base user created in the base user test.
        :return:
        '''
        pass