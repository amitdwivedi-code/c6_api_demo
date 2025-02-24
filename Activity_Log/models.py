from djongo import models

class Activity_Log(models.Model):
    #id = models.IntegerField(primary_key=True,null=False)
    Name = models.CharField(max_length=500, blank=True, null=True)
    Activity = models.CharField(max_length=5000, blank=True, null=True)
    Last_Update = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "Activity_Log"



class BRS_Report_Log(models.Model):
    Financial_Year = models.CharField(max_length=20, blank=True, null=True)
    User_Name = models.CharField(max_length=20, blank=True, null=True)
    Section = models.CharField(max_length=20, blank=True, null=True)
    Last_Update = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "Activity_Log"