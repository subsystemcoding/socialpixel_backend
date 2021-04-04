from django.db import models

class PostVisibilityEnums(models.IntegerChoices):
        ACTIVE = 0
        HIDDEN = 1

class GPSAccuracyEnums(models.IntegerChoices):
        ONEHUNDREDKILOMETERS = 1
        TENKILOMETERS = 10
        ONEKILOMETER = 100
        ONEHUNDREDMETERS = 1000
        TENMETERS = 10000
        ONEMETER = 100000