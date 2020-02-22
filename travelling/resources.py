from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from import_export import resources, fields, instance_loaders
from import_export.widgets import ForeignKeyWidget

from accounts.models import CompanyName
from travelling.models import Trip, Game
from jagdreisencheck.lists import HUNTING_TYPE_LIST, MONTH_LIST, ACCOMODATION_LIST


class TripResource(resources.ModelResource):

    company = fields.Field(column_name='company', attribute='company', widget=ForeignKeyWidget(CompanyName, 'name'))

    def before_import_row(self, row, **kwargs):

        company = row.get('company', None)
        game = row.get('game', None)
        hunting_types = row.get('available_hunting_types', None)
        start_time = row.get('hunting_start_time', None)
        end_time = row.get('hunting_end_time', None)
        accommodation = row.get('available_accommodation_types', None)
        staff_languages = row.get('staff_languages', None)
        # meal_options = row.get('available_meal_options', None)

        print(staff_languages)

        # Transform the company string to a valid foreign key value
        if company is not None:
            cp, cr = CompanyName.objects.get_or_create(name=company)
            # print('{} {} Created: {}'.format(cp.pk, cp.name, cr))
        else:
            raise ValidationError(_('You must provide a company name.'))

        # Transform all comma-separated game types into valid primary keys for the m2m relation.
        if game is not None and type(game) == str:
            gl = game.split(', ')
            res = ''

            for g in gl:
                game, created = Game.objects.get_or_create(name=g)

                if len(res) == 0:
                    res += '{}'.format(game.pk)
                else:
                    res += ', {}'.format(game.pk)

            row.update({'game': res})
        else:
            raise ValidationError(_('You must provide game to hunt.'))

        # Transform the hunting types into valid db values.
        '''
        if hunting_types is not None and type(hunting_types) == str and len(hunting_types) > 0:
            htl = hunting_types.split(", ")
            res = ''

            for e in htl:
                for key, val in HUNTING_TYPE_LIST:
                    if e == val:
                        if len(res) == 0:
                            res += "'{}'".format(key)
                        else:
                            res += ", '{}'".format(key)

            res = "[{}]".format(res)

            row.update({'available_hunting_types': res})

        else:
            raise ValidationError(_('You must provide available hunting types. {} is invalid'.format(hunting_types)))
        '''
        # Transform the month value in a valid date-month.
        if start_time is not None and type(start_time) == str and len(start_time) > 0:
            res = ''

            for key, val in MONTH_LIST:
                if val == start_time:
                    if len(res) == 0:
                        res += '{}'.format(key)
                    else:
                        res += ', {}'.format(key)

            row.update({'hunting_start_time': res})

        # Transform the month value in a valid date-month.
        if end_time is not None and type(end_time) == str and len(end_time) > 0:
            res = ''

            for key, val in MONTH_LIST:
                if val == end_time:
                    if len(res) == 0:
                        res += '{}'.format(key)
                    else:
                        res += ', {}'.format(key)

            row.update({'hunting_end_time': res})

        if accommodation is not None and type(accommodation) == str and len(accommodation) > 0:
            htl = accommodation.split(", ")
            res = ''

            for e in htl:
                for key, val in ACCOMODATION_LIST:
                    if e == val:
                        if len(res) == 0:
                            res += "'{}'".format(key)
                        else:
                            res += ", '{}'".format(key)

            res = "[{}]".format(res)

            row.update({'available_accommodation_types': res})

        if staff_languages is not None and type(staff_languages) == str and len(staff_languages) > 0:
            langs = staff_languages.split(", ")
            res = ''
            for lang in langs:

                if len(res) == 0:
                    res += "'{}'".format(lang)
                else:
                    res += ", '{}'".format(lang)

            res = "[{}]".format(res)

            row.update({'staff_languages': res})

        return row

    def get_instance(self, instance_loader, row):
        params = {}
        company = row.get('company', None)
        country = row.get('country', None)
        region = row.get('region', None)
        try:
            if company:
                field = instance_loader.resource.fields['company']
                params[field.attribute] = field.clean(row)

            if country:
                field = instance_loader.resource.fields['country']
                params[field.attribute] = field.clean(row)

            if region:
                field = instance_loader.resource.fields['region']
                params[field.attribute] = field.clean(row)

            if params:
                return instance_loader.get_queryset().get(**params)
            else:
                return None

        except instance_loader.resource._meta.model.DoesNotExist:
            return None

    def init_instance(self, row=None):
        model = self._meta.model
        return model()

    def save_instance(self, instance, using_transactions=True, dry_run=False):

        self.before_save_instance(instance, using_transactions, dry_run)

        if not using_transactions and dry_run:
            pass
        else:
            instance.consent_to_travel_rules = True
            instance.save()

            print("The trip by {} to {}, {} has been saved. Price lists have been created".format(instance.company.name,
                                                                                                  instance.region,
                                                                                                  instance.country.name))

        self.after_save_instance(instance, using_transactions, dry_run)

    class Meta:
        model = Trip
        skip_unchanged = True
        report_skipped = True
        dry_run = False
        fields = ['company', 'country', 'region', 'game', 'available_hunting_types', 'rifle_rentals',
                  'hunting_start_time', 'hunting_end_time', 'available_accommodation_types', 'alternative_activities',
                  'airport_transfer', 'private_parking', 'staff_languages', 'interpreter_at_site', 'family_offers',
                  'wireless_coverage', 'broadband_internet']