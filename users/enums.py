from django.db import models

class ProfileVisibilityEnums(models.IntegerChoices):
        PUBLIC = 0
        PRIVATE = 1