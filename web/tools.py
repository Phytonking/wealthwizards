from uuid import uuid4
import web.models as wm
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
        account.cash_balance -= amount_needed*1.01
        wealthWizardsAccount.cash_balance += amount_needed*1.01
        return True
    
def checkSharesForSale(fund, amountRequested):
    sharesForSale = wm.Share.objects.filter(fund_of_shares=fund, outstanding=True, sold=False)
    if sharesForSale.count() < amountRequested:
        return False
    else:
        return sharesForSale[0:amountRequested-1]

def mark_sold(shares, new_owner):
    for share in shares:
        share.sold=True
        share.owner = new_owner

def payout(OwnersAndPayouts):
    global wealthWizardsAccount
    for l in OwnersAndPayouts:
        payee = l["owner"]
        wealthWizardsAccount.cash_balance -= l["payout"]
        payee.cash_balance += l["payout"]
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
            amt_needed += x.current_value
        transact = checkCashBalanceAndDeduct(buyer, amt_needed)
        if transact != True:
            return False
        else:
            mark_sold(shares_to_be_purchased, buyer)
        payout(previousOwnersAndPayouts)

        return True



            





