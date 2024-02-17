from django.db import models
from django.contrib.auth.models import User
from uuid import uuid4
#from web.tools import *

# Create your models here.
class Fund(models.Model):
    fund_id = models.UUIDField(null=True)
    name = models.TextField()
    number_of_shares = models.BigIntegerField()
    fund_value = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.number_of_shares} shares - Worth: ${self.fund_value}"

class Account(models.Model):
    user_detail = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="user_account")
    cash_balance = models.DecimalField(max_digits=10, decimal_places=2)
    account_number = models.TextField()
    verified = models.BooleanField()
    plaid_access_token = models.TextField(null=True)
    SSN = models.TextField(null=True)
    DateOfBirth = models.DateField(null=True)
    def __str__(self):
        return f"{self.user_detail.first_name} {self.user_detail.last_name}: {self.account_number}"
    

class Share(models.Model):
    share_id = models.UUIDField(auto_created=True)
    owner = models.ForeignKey(Account, on_delete=models.DO_NOTHING, related_name="owner_of_share", null=True)
    share_price_at_purchase = models.DecimalField(null=True, decimal_places=2, max_digits=10)
    current_value = models.DecimalField(null=True, decimal_places=2, max_digits=10)
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

class TransactionType(models.TextChoices):
    WITHDRAWAL = 'withdrawal', 'Withdrawal'
    DEPOSIT = 'deposit', 'Deposit'
    TRANSFER = 'transfer', 'Transfer'

class Transaction(models.Model):
    money_sender = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="money_sender", null=True)
    money_reciever = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="money_reciever", null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(
        max_length=10,
        choices=TransactionType.choices,
        default=TransactionType.DEPOSIT,
    )
    timestamp = models.DateTimeField(auto_now_add=True)

class OrderType(models.TextChoices):
    BUY="Buy", "buy"
    SELL="Sell", "sell"

class TradeOrder(models.Model):
    orderer = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="personOrdering")
    shares_of = models.ForeignKey(Fund, on_delete=models.DO_NOTHING, related_name="sharesOf")
    trade_type = models.CharField(
        max_length=10,
        choices=OrderType.choices,
        default=OrderType.BUY
    )
    processed=models.BooleanField()
    
    