from django.db import models
from django.core.validators import MinLengthValidator

class newuser(models.Model):
    name=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    password=models.CharField(max_length=500)
    gender=models.CharField(max_length=1)

    class Meta:
        db_table = "loginsys_newuser"

    def register(self):
        self.save()

    @staticmethod
    def get_customer_by_email(email):
        try:
            return newuser.objects.get(email=email)
        except:
            return False


    def isExists(self):
        if newuser.objects.filter(email = self.email):
            return True
        return False

    