from django.db import models
from django.contrib.auth.models import User
from uuid import uuid4
#from web.tools import *

# Create your models here.
class Fund(models.Model):
    fund_id = models.UUIDField(null=True)
    name = models.TextField()
    number_of_shares = models.BigIntegerField()
    fund_value = models.FloatField()

    def __str__(self):
        return f"{self.name} - {self.number_of_shares} shares - Worth: ${self.fund_value}"

class Account(models.Model):
    user_detail = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="user_account")
    cash_balance = models.FloatField()
    account_number = models.TextField()
    verified = models.BooleanField()

    def __str__(self):
        return f"{self.user_detail.first_name} {self.user_detail.last_name}: {self.account_number}"

class Share(models.Model):
    share_id = models.UUIDField(auto_created=True)
    owner = models.ForeignKey(Account, on_delete=models.DO_NOTHING, related_name="owner_of_share", null=True)
    share_price_at_purchase = models.FloatField(null=True)
    current_value = models.FloatField(null=True)
    fund_of_shares = models.ForeignKey(Fund, on_delete=models.DO_NOTHING, related_name="fund_purchased")
    sold = models.BooleanField(null=True)
    outstanding = models.BooleanField(null=True)

    def __str__(self):
        res = f"{self.fund_of_shares.name}, ID: {self.share_id} - Last Purchased at {self.share_price_at_purchase}"
        if self.sold:
            res += " (SOLD)"
        elif self.outstanding:
            res += " (OUTSTANDING)"
        return res
    
class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="for_user")
    one_time_password = models.TextField()
    expired = models.BooleanField()

