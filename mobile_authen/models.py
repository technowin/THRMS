from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    id = models.BigIntegerField( unique=True,primary_key=True)
    username = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, null=True,blank=True )
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    last_login = models.DateTimeField(default=None, null=True, blank=True)
    USERNAME_FIELD = 'username'
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    class Meta:
        db_table = 'user'
class PasswordStorage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    raw_password = models.CharField(max_length=255)
    # Add other fields if needed

    class Meta:
        db_table = 'password_storage'