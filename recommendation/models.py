from django.db import models

# Create your models here.

class RecommendationModel(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    financial_year = models.CharField(max_length=200, blank=True, null=True)
    recommendation_key = models.CharField(max_length=256, blank=True, null=True)
    recommendation_value = models.TextField(blank=True, null=True)