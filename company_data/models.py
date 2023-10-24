from django.db import models


class Company(models.Model):
    crn = models.CharField(max_length=20, null=True, blank=True, unique=True)
    tax_id = models.CharField(max_length=20, null=True, blank=True, unique=False)
    vat_id = models.CharField(max_length=20, null=True, blank=True, unique=False)

    def __str__(self):
        return f'Company({self.crn}, {self.tax_id}, {self.vat_id})'

