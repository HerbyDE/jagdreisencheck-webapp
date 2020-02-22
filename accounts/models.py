from __future__ import unicode_literals

import uuid
import jwt

from ckeditor.fields import RichTextField
from django.core import signing
from django.contrib import auth
from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, Group, Permission
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.validators import ASCIIUsernameValidator, UnicodeUsernameValidator
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.password_validation import password_changed
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db import models
from django.utils import six, timezone, text
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField
from image_optimizer.fields import OptimizedImageField
from languages.fields import LanguageField

from jagdreisencheck.custom_fields import ListField
from jagdreisencheck.global_helpers import validate_upload_size
from jagdreisencheck.lists import *
from newsletter.models import Subscription, Newsletter


# Views & Functions
def update_last_login(sender, user, **kwargs):
    """
    A signal receiver which updates the last_login date for
    the user logging in.
    """
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])


user_logged_in.connect(update_last_login)


# BaseUser Manager
class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('An E-Mail is required')

        user = self.model(
            email=self.normalize_email(email),
            # username=self.normalize_email(email),
            password=password
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email=email,
            password=password
        )
        user.is_staff = True
        user.is_active = True
        user.is_moderator = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        user = self.create_user(
            email=email,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)

        return user

    def create_moderator(self, email, password=None):
        """
        Creates and saves a moderator user with the given email and password.
        """
        user = self.create_user(
            email=email,
            password=password
        )
        user.moderator = True
        user.save(using=self._db)
        return user


# Permissions functions
def _user_get_all_permissions(user, obj):
    permissions = set()
    for backend in auth.get_backends():
        if hasattr(backend, "get_all_permissions"):
            permissions.update(backend.get_all_permissions(user, obj))
    return permissions


def _user_has_perm(user, perm, obj):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends():
        if not hasattr(backend, 'has_perm'):
            continue
        try:
            if backend.has_perm(user, perm, obj):
                return True
        except PermissionDenied:
            return False
    return False


def _user_has_module_perms(user, app_label):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends():
        if not hasattr(backend, 'has_module_perms'):
            continue
        try:
            if backend.has_module_perms(user, app_label):
                return True
        except PermissionDenied:
            return False
    return False


usernameValidators = UnicodeUsernameValidator() if six.PY3 else ASCIIUsernameValidator()


def generate_short_uuid4():
    # Collision probability: 0.00000000000000000001%. Evaded by setting the id to unique.
    uid = uuid.uuid4()
    short = uid.time_low
    key = hex(int(short))[2:]

    return key


def generate_activation_token(user=None):
    user = user.email
    token_content = {
        'user': user,
        'iat': timezone.now(),
        'exp': timezone.now() + timezone.timedelta(days=2)
    }

    token = jwt.encode(payload=token_content, key=settings.REG_KEY, algorithm='HS256')

    result = {
        'status': 1,
        'token': token
    }

    return result


# BaseUser
class AbstractUser(AbstractBaseUser, auth.models.PermissionsMixin):
    id = models.CharField(primary_key=True, editable=False, max_length=10)
    email = models.EmailField(verbose_name=_('E-Mail'), max_length=70, unique=True,
                              help_text=_('Please provide your e-mail address that you will use to log in.'),
                              error_messages={'unique': _('User with this e-mail already exists.')})
    # username = models.CharField(verbose_name=_('Username'), max_length=150, blank=False, null=False,
    # unique=True, validators=[usernameValidators])
    password = models.CharField(_('password'), max_length=128,
                                help_text=_('Please provide your password here. It must contain at least 1 letter, 1 '
                                            'numeric character and one special character (e.g. ?). The minimum length '
                                            'is 8 characters.'))
    role = models.CharField(max_length=100, blank=True, null=True, default=None, verbose_name=_('Profile Slogan'))
    is_company = models.BooleanField(default=False, verbose_name=_('Account Type'), choices=ISCompanyList)
    is_active = models.BooleanField(default=False, verbose_name=_('Active'), choices=YNList)
    is_moderator = models.BooleanField(default=False, verbose_name=_('Moderator'))
    is_staff = models.BooleanField(default=False, verbose_name=_('Staff'))
    date_joined = models.DateTimeField(verbose_name=_('Join Date'), default=timezone.now)
    last_login = models.DateTimeField(verbose_name=_('Last Login'), default=timezone.now)
    first_name = models.CharField(verbose_name=_('First Name'), max_length=150, blank=False, null=False)
    last_name = models.CharField(verbose_name=_('Last Name'), max_length=70, blank=True, null=True)
    company_name = models.CharField(verbose_name=_('Company Name'), max_length=120, blank=True, null=True)
    country_of_residence = CountryField(verbose_name=_('Home Country'), max_length=120, blank=False, null=False,
                                        help_text=_("Please provide the country you're living in here."), default="DE")
    activation_key = models.CharField(verbose_name=_('Activation Token'), max_length=300, blank=False, null=True)
    reset_token = models.CharField(verbose_name=_('Reset Token'), max_length=300, blank=True, null=True)
    share_link = models.CharField(verbose_name=_('Share Link'), max_length=300, blank=True, null=True)
    numeric_key = models.IntegerField(verbose_name=_('Numeric Key'), blank=True, null=True)
    agree_to_tos = models.BooleanField(verbose_name=_('Terms of Service'), blank=False, default=False, choices=YNList)
    agree_to_privacy = models.BooleanField(verbose_name=_('Privacy Terms'), blank=False, default=False, choices=YNList)
    allowed_inquiries = models.IntegerField(verbose_name=_('Remaining Inquiries'), blank=False, default=5)
    next_inquiries_date = models.DateField(verbose_name=_('Next Inquiries'), blank=True, null=True)

    editor = models.ForeignKey(verbose_name=_('Editor for a Company'), to='accounts.CorporateProfile',
                               null=True, blank=True, on_delete=models.SET_NULL)
    editor_permissions = models.IntegerField(verbose_name=_('Editor Permissions'), default=0, blank=False)

    # Referrals
    referral_code = models.CharField(verbose_name=_('Referral Code'), max_length=100, blank=True, null=True)
    referred_by = models.CharField(verbose_name=_('Referred By - Code'), max_length=100, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    EMAIL_FIELD = 'email'

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        abstract = True

    def save(self, *args, **kwargs):

        # Custom primary key
        if not self.pk:
            self.pk = generate_short_uuid4()

        # Generate Password and a valid activation token
        if not self.activation_key:
            self.activation_key = generate_activation_token(self)

        if self._password is not None:
            password_changed(self._password, self)
            self._password = None

        # Referral Code Signature
        if not self.referral_code:
            signer = signing.Signer()
            ref = signer.sign(self.pk)

            self.referral_code = ref.split(":")[1]

        return super(AbstractUser, self).save(*args, **kwargs)

    def set_get_username(self):
        if self.username:
            return self.username
        else:
            self.username = self.email
            return self.email

    def get_full_name(self):
        # Either returns the company name or the full name if not 'is company'
        if self.is_company:
            return self.company_name
        else:
            return u'%s %s' % (self.first_name, self.last_name)

    def get_short_name(self):
        # Either returns the company name or the full name if not 'is company'
        if self.is_company:
            return self.company_name
        else:
            return self.first_name

    def has_password_reset_token(self):
        if self.reset_token:
            return True
        else:
            return False

    def get_url_slug(self):
        if self.is_company:
            url = '/accounts/%s' % text.slugify(self.company_name, allow_unicode=True)

            return url
        else:
            url = '%s %s %s' % (self.first_name, self.last_name, self.pk)
            url = '/accounts/%s' % text.slugify(url)

            return url

    def send_mail_to_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to the user
        '''
        return send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):  # __unicode__ on Python 2
        return self.email


class User(AbstractUser):
    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'
        app_label = 'accounts'
        db_table = 'auth_user'
        verbose_name = _('User')
        verbose_name_plural = _('Users')


class IndividualProfile(models.Model):
    id = models.CharField(primary_key=True, editable=False, max_length=10,
                          help_text=_('The ID must match the ID of its associated user'))
    user = models.ForeignKey(verbose_name=_('Associated User'), to='accounts.User', on_delete=models.CASCADE,
                             db_index=True)
    gender = models.CharField(verbose_name=_('Gender'), blank=False, null=True, max_length=2, choices=GENDER_LIST)
    birth_date = models.DateField(verbose_name=_('Date of Birth'), blank=False, null=True, error_messages={
        'invalid': _('Please provide a valid date. Format: dd.mm.yyyy')
    })
    hunting_license = models.BooleanField(verbose_name=_('Hunting Licence'), blank=False, choices=YNList,
                                          help_text=_("Please indicate if you own a hunting license. This is required as we focus on sustainable hunting and that includes that hunters that use our platform must have a formal qualification for hunting."))
    years_as_active_hunter = models.IntegerField(verbose_name=_('Active hunter since'), blank=True, null=True,
                                                 choices=YEAR_LIST())
    countries_visited_for_hunting = CountryField(verbose_name=_('Countries Visited for Hunting'), blank=True,
                                                 multiple=True)
    preferred_hunting_type = models.CharField(verbose_name=_('Preferred Hunting Type'), blank=True, null=True,
                                              choices=HUNTING_TYPE_LIST, max_length=2)
    preferred_rifle_type = models.CharField(verbose_name=_('Preferred Rifle Type'), blank=True, null=True,
                                            max_length=75)
    info = RichTextField(verbose_name=_('Personal Information'), blank=True, null=True)

    # File Fields
    profile_pic_height = models.IntegerField(null=True)
    profile_pic_width = models.IntegerField(null=True)
    profile_pic = OptimizedImageField(verbose_name=_('Profile Picture'), upload_to="profile_pictures/", blank=True,
                                      null=True, height_field='profile_pic_height', width_field='profile_pic_width',
                                      validators=[validate_upload_size])

    title_pic = OptimizedImageField(verbose_name=_('Title Image'), upload_to="title_images/", blank=True,
                                    null=True)
    headline_image_position = models.IntegerField(verbose_name=_('Title Picture Position'), null=True, default=0)

    # Settings
    profile_visibility = models.BooleanField(verbose_name=_('Profile Visibility'), blank=False, null=False,
                                             default=True, choices=YNList)
    search_visibility = models.BooleanField(verbose_name=_('Visibility in internal Search'), blank=False, null=False,
                                            default=True, choices=YNList)
    profile_pic_visibility = models.CharField(verbose_name=_('Profile Picture Visibility'), blank=False, null=False,
                                              default='M', choices=VISIBILITY_LIST, max_length=2)
    title_pic_visibility = models.CharField(verbose_name=_('Title Image Visibility'), blank=False, null=False,
                                            default='M', choices=VISIBILITY_LIST, max_length=2)
    email_visibility = models.CharField(verbose_name=_('E-Mail Visibility'), blank=False, null=False,
                                        default='N', choices=VISIBILITY_LIST, max_length=1)
    email_newsletter = models.CharField(verbose_name=_('News on Jagdreisencheck'), blank=False, null=False,
                                        default='M', choices=NEWSLETTER_LIST, max_length=1)

    # GDPR-related data
    data_dump_requested = models.BooleanField(verbose_name=_('Data Dump Request'), blank=False, default=False,
                                              choices=YNList)
    data_dump_date = models.DateField(verbose_name=_('Last Data Dump'), blank=True, null=True)
    data_dump_count = models.IntegerField(verbose_name=_('Data Dump Request Counter'), blank=False, default=0)

    def save(self, *args, **kwargs):

        if self.email_newsletter == 'M':

            try:
                newsletter = Newsletter.objects.get(slug='jagdpost')
                subscription = Subscription.objects.get_or_create(user=self.user, newsletter=newsletter)[0]
                subscription.subscribed = True
                subscription.subscribe_date = datetime.now()
                subscription.unsubscribed = False
                subscription.subscribe_date = None
                subscription.save()

            except Newsletter.DoesNotExist:
                pass

        elif self.email_newsletter == 'I':

            try:
                subscription = Subscription.objects.get(user=self.user)
                subscription.subscribed = False
                subscription.subscribe_date = None
                subscription.unsubscribed = True
                subscription.subscribe_date = datetime.now()
                subscription.save()

            except Subscription.DoesNotExist:
                pass

        return super(IndividualProfile, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = _('Individual Profile')
        verbose_name_plural = _('Individual Profiles')


class CompanyName(models.Model):
    id = models.CharField(primary_key=True, editable=False, max_length=10,
                          help_text=_('The ID must match the ID of its associated user'))
    name = models.CharField(verbose_name=_('Company Name'), blank=False, null=False, max_length=150, unique=True)
    contact_email = models.EmailField(verbose_name=_('Contact E-Mail'), blank=True, null=True, unique=True,
                                      help_text=_("Please provide the company's public email address where potential customers can contact you."))
    created_by = models.ForeignKey(verbose_name=_('Creator'), blank=True, null=True, to=User,
                                   on_delete=models.SET_NULL)
    created_at = models.DateTimeField(verbose_name=_('Creation Date'), blank=False, auto_now_add=True, editable=True)
    has_profile = models.BooleanField(verbose_name=_('Has Corporate Profile'), blank=False, null=False, default=False)

    slug = models.SlugField(verbose_name=_('Slug'), blank=False, null=True)
    logo = OptimizedImageField(verbose_name=_('Logo'), upload_to="company_logos/", blank=True,
                               null=True, height_field='logo_height', width_field='logo_width',
                               validators=[validate_upload_size])
    logo_height = models.IntegerField(null=True)
    logo_width = models.IntegerField(null=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        if not self.id:
            self.id = generate_short_uuid4()

        if not self.slug:
            self.slug = text.slugify(self.name)

        return super(CompanyName, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return u'%s' % str(self.name)

    class Meta:
        verbose_name = _('Company Name')
        verbose_name_plural = _('Company Names')
        ordering = ['name']


class CorporateProfile(models.Model):
    id = models.CharField(primary_key=True, editable=False, max_length=10,
                          help_text=_('The ID must match the ID of its associated user'))
    company_name = models.ForeignKey(verbose_name=_('Company Name'), to=CompanyName, on_delete=models.CASCADE)
    operator_type = models.CharField(verbose_name=_('Are you a travel agent or direct provider?'), blank=False, null=True,
                                     choices=OPERATOR_TYPE, max_length=8, default='AGENT')
    admin = models.ForeignKey(verbose_name=_('Company Administrator'), to=User, on_delete=models.SET_NULL, null=True)
    # Address Information
    address = models.CharField(verbose_name=_('Address'), max_length=100, blank=False)
    zip_code = models.CharField(verbose_name=_('ZIP Code'), max_length=7, blank=False)
    city = models.CharField(verbose_name=_('City'), max_length=75, blank=False)
    country = CountryField(verbose_name=_('Country'), default="DE",
                           help_text=_("This is the country where your firm's headquarter is in."))
    main_lang_of_conversation = LanguageField(verbose_name=_("Your primary language for conversations"), default="de",
                                              blank=False, null=True)
    # Contact Information
    phone = models.CharField(verbose_name=_('Phone'), max_length=50, blank=False,
                             help_text=_('Please provide your public phone number. Please DO NOT use country codes, '
                                         'instead provide the local format: 01234 000000000. Characters "+" and "/" '
                                         'are NOT allowed.' ))
    contact_email = models.EmailField(verbose_name=_('Contact E-Mail'), blank=False)
    business_hours_days = ListField(verbose_name=_('Days the business is open'), blank=False)
    business_hours_start = models.TimeField(verbose_name=_('Business Hours Start'), blank=True, null=True)
    business_hours_end = models.TimeField(verbose_name=_('Business Hours End'), blank=True, null=True)
    business_hours_break_start = models.TimeField(verbose_name=_('Lunch Break Start'), blank=True, null=True)
    business_hours_break_end = models.TimeField(verbose_name=_('Lunch Break End'), blank=True, null=True)

    # Profile Information
    description = models.TextField(verbose_name=_('Description'), max_length=3000, blank=True, null=True)
    homepage = models.CharField(verbose_name=_('Homepage'), blank=True, null=True, max_length=75)

    title_pic = OptimizedImageField(verbose_name=_('Title Image'), upload_to="title_images/", blank=True,
                                    null=True)
    headline_image_position = models.IntegerField(verbose_name=_('Title Picture Position'), null=True, default=0)

    # Admin Data
    date_joined = models.DateTimeField(verbose_name=_('Date Joined'), auto_now_add=True)
    last_modified = models.DateTimeField(verbose_name=_('Last modified'), auto_now_add=True, null=True, blank=True)
    has_lead_contract = models.BooleanField(verbose_name=_('Contracted for leads'), default=False, choices=YNList)
    
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        
        self.pk = self.admin.pk
        self.last_modified = timezone.now()
        
        return super(CorporateProfile, self).save(force_insert, force_update, using, update_fields)
        
    def __str__(self):
        return self.company_name.name


class Group(Group):
    pass


class Permission(Permission):
    pass