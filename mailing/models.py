from django.utils.text import slugify
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
import os
from django.core.exceptions import ValidationError

from jagdreisencheck.custom_fields import ListField


# File field validator
def validate_pdf(file):
    ext = os.path.splitext(file.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf']

    if not ext.lower() in valid_extensions:
        raise ValidationError(_('Disallowed file extension. Only PDF is allowed.'))


# Create your models here.
class CustomerLoyaltyElement(models.Model):
    name = models.CharField(verbose_name=_('Title'), max_length=150, blank=False, null=True, editable=False)
    link_description = models.CharField(verbose_name=_('Link description'), max_length=150, blank=False, null=True)
    description = models.TextField(verbose_name=_('Text to display on the user page'), blank=True, null=True)
    file = models.FileField(verbose_name=_('File'), upload_to='loyalty/', validators=[validate_pdf], null=True)
    corporate = models.BooleanField(verbose_name=_('For corporate users'), default=False)
    date_created = models.DateTimeField(verbose_name=_('Date Created'), auto_now_add=True)
    date_modified = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Customer Loyalty Element')
        verbose_name_plural = _('Customer Loyalty Elements')


class CustomerLoyaltyCheck(models.Model):

    file = models.ForeignKey(verbose_name=_('Associated File'), to=CustomerLoyaltyElement, on_delete=models.CASCADE)
    user = models.ForeignKey(verbose_name=_('User'), to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_created = models.DateTimeField(verbose_name=_('Date Created'), auto_now_add=True)

    def __str__(self):
        return u'%s - %s' % (self.file.name, self.user.pk)


class MailingList(models.Model):
    name = models.CharField(verbose_name=_('Title'), max_length=150, blank=False, null=True)
    subscribers = models.ManyToManyField(verbose_name=_('Subscribers'), to=settings.AUTH_USER_MODEL)

    date_created = models.DateTimeField(verbose_name=_('Date Created'), auto_now_add=True)
    date_modified = models.DateTimeField()

    @property
    def get_slug(self):
        return slugify(self.name)

    def __str__(self):
        return self.name


class Mail(models.Model):
    title = models.CharField(verbose_name=_('Mail Title'), max_length=255)
    body = models.TextField(verbose_name=_('Mail Body'))
    variant = models.CharField(verbose_name=_('E-Mail Variant'), max_length=3, default='MAS',
                               choices=[('MAS', _('Send Bulk E-Mail')), ('IND', _('Send E-Mails Individually'))])

    date_created = models.DateTimeField(verbose_name=_('Date Created'), auto_now_add=True)
    author = models.ForeignKey(verbose_name=_('Author'), to='accounts.User', on_delete=models.SET_NULL, null=True)
    target = models.ForeignKey(verbose_name=_('Mailing List'), to=MailingList, on_delete=models.SET_NULL, null=True)
    sent = models.BooleanField(verbose_name=_('Mail Sent'), default=False)

    def __str__(self):
        return u'%s - %s' % (self.title, self.target.name)


class Attachment(models.Model):
    file = models.FileField(verbose_name=_('Attachment File'), upload_to="mail/attachments/")
    email = models.ForeignKey(verbose_name=_('E-Mail'), to=Mail, on_delete=models.CASCADE)

    def __str__(self):
        file_name = self.file.name

        return u'%s - %s' % (file_name, self.email.title)