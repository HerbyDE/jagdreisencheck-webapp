from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def get_upload_path(key, folder):
    path = '%s/%s/%s' % ('media', key, folder)
    return path


def validate_upload_size(val):
    limit = settings.MAX_UPLOAD_SIZE
    
    if val.size > limit:
        raise ValidationError(_('File too large. Size should not exceed 2 MiB.'))
