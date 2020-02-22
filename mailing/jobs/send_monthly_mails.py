from django.utils.translation import ugettext_lazy as _

from django_cron import CronJobBase, Schedule
from mailing.views import send_mail

from travelling.models import Trip
from inquiries.models import TripInquiry


class SendStatistics(CronJobBase):
    runtime = 1  # in Minutes
    schedule = Schedule(run_every_mins=runtime)
    code = 'jobs.SendStatistics'
    
    def do(self):
        template = 'mailing/jobs/test-mail.html'
        return send_mail(subject=_('Testmail'), recipients=['herbert.woisetschlaeger@jagdreisencheck.de'],
                         context={'test', 'YCMK123'}, html_template=template)
