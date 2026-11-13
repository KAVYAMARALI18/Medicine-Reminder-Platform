from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class SpaceAllowedUsernameValidator(UnicodeUsernameValidator):
    regex = r"^[\w.@+-]+(?: +[\w.@+-]+)*\Z"
    message = _(
        "Enter a valid username. Use letters, numbers, spaces, and @/./+/-/_ characters."
    )
    flags = 0
