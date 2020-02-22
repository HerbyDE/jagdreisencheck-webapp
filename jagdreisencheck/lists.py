from datetime import datetime

from django.utils.translation import ugettext_lazy as _

# All Jagdreisencheck lists
ISCompanyList = (
    (1, _('Company')),
    (0, _('User'))
)

YNList = (
    (False, _('No')),
    (True, _('Yes'))
)

YNNList = (
    (0, _('No')),
    (1, _('Yes')),
    (2, _('Unknown'))
)

# Accounts Lists
GENDER_LIST = (
    ('M', _('Male')),
    ('F', _('Female')),
    ('O', _('Other')),
    ('X', _('No information')),
)

VISIBILITY_LIST = (
    ('E', _('Everyone')),
    ('M', _('Logged-in Users Only')),
    # ('C'), _('Linked Users'),
    ('N', _('Nobody'))
)

NEWSLETTER_LIST = (
    # ('W', _('Weekly')),
    ('M', _('Important E-Mails + Newsletter')),
    ('I', _('Important E-Mails only')),
    # ('N', _('No E-Mails'))
)

INQUIRY_LIST = (
    ("ST", _("Solo Travel")),
    ("GT", _("Group Travel")),
    ("OT", _("Other"))
)

# Travel Lists
ACCOMODATION_LIST = (
    ('SO', _('Self Organized')),
    ('CA', _('Camping')),
    ('CO', _('Simple Cottage')),
    ('HH', _('Holiday Home / Hunting Chalet')),
    ('LO', _('Lodge')),
    ('HC', _('Hunting Chalet')),
    ('HO', _('Hotel'))
)

MEAL_LIST = (
    ('N', _('No Meals Included')),
    ('B', _('Breakfast Only')),
    ('H', _('Half Board')),
    ('A', _('All Inclusive'))
)

DOG_CHOICE_LIST = (
    ('NH', _('Chasing Dogs')),
    ('DR', _('Joint Hunt')),
    ('PI', _('Stalking Support')),
)

HUNTING_TYPE_LIST = (
    ('P', _('Stalking')),
    ('A', _('Stand Hunting')),
    ('G', _('Joint Hunting')),
    # ('B', _('Bow Hunt'))
)

MONTH_LIST = (
    (1, _('January')),
    (2, _('February')),
    (3, _('March')),
    (4, _('April')),
    (5, _('May')),
    (6, _('June')),
    (7, _('July')),
    (8, _('August')),
    (9, _('September')),
    (10, _('October')),
    (11, _('November')),
    (12, _('December')),
)

DAY_CHOICE_LIST = (
    ('MON', _('Monday')),
    ('TUE', _('Tuesday')),
    ('WED', _('Wednesday')),
    ('THU', _('Thursday')),
    ('FRI', _('Friday')),
    ('SAT', _('Saturday')),
    ('SUN', _('Sunday')),
)

ONE_TO_FIVE_LIST = (
    (1, _('Bad')),
    (2, _('Rather Bad')),
    (3, _('Neutral')),
    (4, _('Rather Good')),
    (5, _('Good')),
)

FITNESS_LIST = (
    (1, _('less than 1km walking distance per day')),
    (2, _('between 1km and up to 2.5km walking distance per day')),
    (3, _('between 2.5km and up to 5km walking distance per day')),
    (4, _('between 5km and up to 10km walking distance per day')),
    (5, _('more than 10km walking distance per day')),
)

EXPERIENCE_LIST = (
    (1, _('Suitable for beginners (< 2 years experience)')),
    (2, _('Suitable for hunters with little experience (> 2 years & < 4 years)')),
    (3, _('Suitable for hunters with some experience (> 4 years & < 5 years)')),
    (4, _('Suitable for hunters with good experience (> 5 years & < 7 years)')),
    (5, _('Suitable for hunters with extensive experience (> 7 years)')),
)

GAME_GENDER_LIST = (
    ('F', _('Female')),
    ('M', _('Male')),
    ('Y', _('Young')),
    ('X', _('No information')),
)

GAME_DENSE_LIST = (
    (1, _('Too sparse')),
    (3, _('Rather too sparse')),
    (5, _('Optimal density')),
    (3, _('Rather too dense')),
    (1, _('Too dense')),
    (0, _('Unknown'))
)

GAME_AGE_DIST_LIST = (
    (1, _('Too young')),
    (3, _('Rather too young')),
    (5, _('Optimal')),
    (3, _('Rather too old')),
    (1, _('Too old')),
    (0, _('Unknown'))
)

GAME_GENDER_DIST_LIST = (
    (1, _('Predominantly female game')),
    (3, _('Slight overweight of female game')),
    (5, _('Good gender distribution')),
    (3, _('Slight overweight of male game')),
    (1, _('Predominantly male game')),
    (0, _('Unknown'))
)

INDICATION_LIST = (
    (1, _('Definitely no')),
    (2, _('Rather no')),
    (3, _("Don't know")),
    (4, _('Rather yes')),
    (5, _('Definitely yes')),
)


def YEAR_LIST(min_year=0):
    current_year = datetime.now().year
    year = int(current_year) - min_year
    start_year = int(current_year) - 100
    li = list()
    while year > start_year:
        li.append((year, year))
        year -= 1

    return li


CALCULATION_TYPE_LIST = [
    ('CIC', _('CIC points')),
    ('PCS', _('Pieces')),
    ('KGS', _('kg')),
    ('LEN', _('Length (in cm)')),
    ('AGE', _('Age class')),
]


TRAVELLER_CHOICE_LIST = [
    ('OP', _('Open')),
    ('FC', _('First contact')),
    ('OS', _('Offer sent')),
    ('FU', _('Follow up required')),
    ('OA', _('Offer accepted')),
    ('PR', _('Payment received')),
    ('CT', _('Customer on trip')),
    ('CT', _('Customer returned')),
    ('IR', _('Customer invited for review')),
    ('RR', _('Review received')),
    ('CL', _('Closed')),
]


OPERATOR_TYPE = [
    ('AGENT', _('Travel Agent')),
    ('PROVIDER', _('Travel Provider')),
]


BILLING_PERIOD = [
    ('D', _('Per day')),
    ('W', _('Per week')),
    ('M', _('Per month')),
    ('S', _('Per stay')),
    ('O', _('Other'))
]


GAME_BILLING_RANGE = [
    ('G', _('Per gram')),
    ('L', _('Per centimeter')),
    ('P', _('Per piece')),
    ('C', _('CIC points')),
    ('A', _('Age class')),
    ('O', _('Other range'))
]


# Lead Status
LEAD_STATUS_LIST = [
    (1, _('Active')),
    (0, _('Permanently inactive')),
    (2, _('Capacity limit reached for this season')),
]


# Plugin Lists
REGISTRATION_TYPE_LIST = (
    ('C', _('Corporate')),
    ('I', _('User/Consumer'))
)
