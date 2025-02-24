from djongo import models


class Descriptions(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Module_Name = models.CharField(max_length=200, blank=True, null=True)
    Heading = models.CharField(max_length=200, blank=True, null=True)
    Description = models.CharField(max_length=5000, blank=True, null=True)

class DescriptionsProjectandPolicies(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    Module_Name = models.CharField(max_length=200, blank=True, null=True)
    Heading = models.CharField(max_length=200, blank=True, null=True)
    Description = models.CharField(max_length=5000, blank=True, null=True)    