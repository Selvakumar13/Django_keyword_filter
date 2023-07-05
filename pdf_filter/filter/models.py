from django.db import models

class Urls(models.Model):
    Url=models.URLField(unique=True)
    keyword=models.CharField(max_length=255)
    keyword_found=models.BooleanField(default=False)
    def __str__( self ):
        return self.Url

    class Meta:
        verbose_name_plural='Entered_Url'