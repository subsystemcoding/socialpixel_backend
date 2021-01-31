from django.db import models

class VisibilityEnums(models.IntegerChoices):
        ACTIVE = 0
        HIDDEN = 1