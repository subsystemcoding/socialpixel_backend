from django.db import models

class PostVisibilityEnums(models.IntegerChoices):
        ACTIVE = 0
        HIDDEN = 1