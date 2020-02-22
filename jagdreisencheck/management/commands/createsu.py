from django.core.management.base import BaseCommand

from accounts.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        if not User.objects.filter(email='waidmann@jagdreisencheck.de').exists():
            User.objects.create_superuser(email='waidmann@jagdreisencheck.de', password='jrc2018!')