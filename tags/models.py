from django.db import models

class Tag(models.Model):

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['-created_on']

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=256, unique=True)
    description = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return str(self.id) + ':' + str(self.name)