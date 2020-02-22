import os
from django.core.management.base import BaseCommand
from django.core.mail import send_mail


from mailing.models import CustomerLoyaltyElement


class Command(BaseCommand):

    def handle(self, *args, **options):

        if not CustomerLoyaltyElement.objects.filter(pk=1).exists():
            CustomerLoyaltyElement.objects.create(
                pk=1,
                name='Unternehmergoodie',
                corporate=True,
                link_description='Marktstudie zur Jagdreiseindustrie in Deutschland (2018) herunterladen'
            )

        if not CustomerLoyaltyElement.objects.filter(pk=2).exists():
            CustomerLoyaltyElement.objects.create(pk=2, name='Jägergoodie', corporate=False)
