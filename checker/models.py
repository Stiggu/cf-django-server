from django.db import models


# Modelo de contratos
class Contracts(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()


# Modelo de rates
class Rates(models.Model):
    contract = models.ForeignKey(Contracts, on_delete=models.CASCADE, related_name='rates')
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    currency = models.CharField(max_length=255)
    twenty = models.CharField(max_length=255)
    forty = models.CharField(max_length=255)
    fortyhc = models.CharField(max_length=255)
