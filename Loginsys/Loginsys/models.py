from django.db import models
from django.core.validators import MinLengthValidator

class newuser(models.Model):
    id = models.AutoField(primary_key=True)
    name=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    password=models.CharField(max_length=500)
    cpassword=models.CharField(max_length=500)
    gender=models.CharField(max_length=1)
    expenses=models.CharField(max_length=100)

    class Meta:
        db_table = "loginsys_newuser"

    def __str__(self):
        return self.email

    @staticmethod
    def get_user_by_email(email):
        try:
            return newuser.objects.get(email=email)
        except:
            return False


    def isExists(self):
        if newuser.objects.filter(email = self.email):
            return True
        return False

    