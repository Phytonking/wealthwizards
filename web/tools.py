from uuid import uuid4
import web.models as wm
from django.core.mail import send_mail
from django_otp import devices_for_user
from datetime import *
wealthWizardsAccount = wm.Account.objects.get(account_number="7942987610154218")


def generate_fund_shares(fund, amountOfShares):
    if amountOfShares == None:
        amountOfShares = fund.number_of_shares
    for x in range(amountOfShares):
        new_share_id = uuid4()
        share_price = float(fund.fund_value/amountOfShares)
        while wm.Share.objects.filter(share_id=new_share_id).count() != 0:
            new_share_id = uuid4()
        l = wm.Share(share_id=new_share_id, owner=wealthWizardsAccount, current_value=share_price, share_price_at_purchase = None, sold=False, fund_of_shares=fund, outstanding=True) 
        l.save()


def update_valuation(fund):
    i = wm.Share.objects.filter(fund_of_shares=fund)
    fund_val = fund.fund_value
    share_val = float(fund_val/i.count())
    for x in i:
        x.current_value = share_val
        x.save()

def share_valuation_update(fund):
    for x in wm.Fund.objects.all():
        update_valuation(x)

def is_over_18(birth_date):
    current_date = datetime.now()
    birth_date = datetime.strptime(birth_date, '%Y-%m-%d')
    age = current_date.year - birth_date.year - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))
    return age >= 18

# processing purchases

"""
When a new purchase is made the following must be done

1. Check to make sure the buyer has enough cash balance, if not cancel the order.
2. Make sure enough shares are available for sale, if not cancel the order.
3. Deduct the cash-balance from the buyer and transfer it to WealthWizards

4. transfer ownership of the shares over to the buyer
    - Edit the owner of the share to the new owner. 
    - if a processing error happens, return the cash-balance over and cancel the order

5. Transfer the previous owner of the shares the funds of the transaction over. 

"""



def checkCashBalanceAndDeduct(account, amount_needed):
    if account.cash_balance < amount_needed:
        return False
    else:
        account.cash_balance = float(account.cash_balance)-float(amount_needed)
        wealthWizardsAccount.cash_balance = float(amount_needed) + float(account.cash_balance)
        return True
    
def checkSharesForSale(fund, amountRequested: int):
    sharesForSale = wm.Share.objects.filter(fund_of_shares=fund, outstanding=True, sold=False)
    if sharesForSale.count() < amountRequested:
        return []
    else:
        return sharesForSale[0:amountRequested-1]

def mark_sold(shares, new_owner):
    for share in shares:
        share.sold=True
        share.owner = new_owner
        share.outstanding = False

def payout(OwnersAndPayouts):
    global wealthWizardsAccount
    for l in OwnersAndPayouts:
        payee = l["owner"]
        wealthWizardsAccount.cash_balance = float(wealthWizardsAccount.cash_balance)-float(l["payout"])
        payee.cash_balance = float(payee.cash_balance) + float(l["payout"])
        payee.save()


def process_purchase(buyer: wm.Account, fund: wm.Fund, numberOfShares: int):
    previousOwnersAndPayouts = []
    shares_to_be_purchased = checkSharesForSale(fund, numberOfShares)
    if shares_to_be_purchased == False:
        return False
    else:
        amt_needed = 0.00
        for x in shares_to_be_purchased:
            previousOwnersAndPayouts.append({"owner": x.owner, "payout": x.current_value})
            amt_needed = float(amt_needed + float(x.current_value))
        transact = checkCashBalanceAndDeduct(buyer, amt_needed)
        if transact != True:
            return False
        else:
            mark_sold(shares_to_be_purchased, buyer)
        payout(previousOwnersAndPayouts)

        return True



#OTP WORK            

import time
import hmac
import hashlib

def generate_OTP(secret_key, time_step=30, digits=6):
    """
    Generate a basic One-Time Password (OTP) based on time.

    Parameters:
        secret_key (str): The secret key shared between the server and the user.
        time_step (int, optional): The time step in seconds. Default is 30 seconds.
        digits (int, optional): The number of digits in the OTP. Default is 6.

    Returns:
        str: The generated OTP.
    """
    # Get the current time in seconds
    current_time = int(time.time())
    # Calculate the number of time steps that have passed since the epoch
    time_steps = current_time // time_step
    # Convert the time steps to bytes
    time_steps_bytes = time_steps.to_bytes(8, 'big')
    #Convert the secret key to bytes
    secret_key_bytes = secret_key.encode('utf-8')
    # Calculate the HMAC-SHA-1 of the time steps using the secret key
    hmac_result = hmac.new(secret_key_bytes, time_steps_bytes, hashlib.sha1).digest()
    # Get the offset value from the last 4 bits of the HMAC result
    offset = hmac_result[-1] & 0x0F
    # Extract a 4-byte integer from the HMAC result based on the offset
    truncated_hash = hmac_result[offset:offset+4]
    # Convert the 4-byte integer to a six-digit OTP
    otp = int.from_bytes(truncated_hash, 'big') % (10 ** digits)
    return str(otp).zfill(digits)







def send_otp_email(user: wm.User, otp: wm.OTP):
    # Generate a one-time code
    # Send the one-time code via email
    subject = 'Your One-Time Code for 2FA'
    message = f'Your one-time code is: {otp.one_time_password}'
    from_email = 'avi.agola@outlook.com'  # Replace with your email
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)
    print("Email Sent Successfully")


