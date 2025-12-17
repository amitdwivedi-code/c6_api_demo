from django.db import models

# Create your models here.

class RecommendationModel(models.Model):
    id = models.IntegerField(primary_key=True,null=False)
    financial_year = models.CharField(max_length=200, blank=True, null=True)
    recommendation_key = models.CharField(max_length=256, blank=True, null=True)
    recommendation_value = models.TextField(blank=True, null=True)


class SOPDocument(models.Model):
    # id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='sop_documents/', null=False, blank=False)
    uploaded_by = models.IntegerField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sop_documents"


