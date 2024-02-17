from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from web.models import *
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.decorators import login_required
from web.tools import *
from uuid import *
from datetime import *

# Create your views here.
def index(request: HttpRequest):
    return render(request, "extratemplates/index.html")

def login_view(request: HttpRequest):
    if request.method == "GET":
        return render(request, "extratemplates/login.html")
    else:
        username = request.POST["username"]
        password = request.POST["password"]
        try:
            us = User.objects.get(username=username)
        except User.DoesNotExist:
            return render(request, "extratemplates/login.html", {"error": "User does not exist"})
        au = authenticate(username=username, password=password)
        if au is not None:
            login(request, us)
            return HttpResponseRedirect(reverse("web:index"))
        else:
            return render(request, "extratemplates/login.html", {"error": "Incorrect Username or Password"})
        

def register_view(request: HttpRequest):
    if request.method == "GET":
        return render(request, "extratemplates/register.html")
    else:
        # add connections to Plaid
        #account holder
        fName = request.POST["first_name"]
        lName = request.POST["last_name"]
        email = request.POST["email"]
        Tele = request.POST["telephone"]
        #DOB = request.POST["DOB"]
        #SSN = request.POST["SSN"]
        username = request.POST["username"]
        password = request.POST["password"]
        #bank = {"name":request.POST["bankName"], "bankAccNum":request.POST["bankAccNum"], "bankRoutNum":request.POST["bankRoutNum"]}
        """
        if is_over_18(DOB) == False:
            ParentfName = request.POST["parent_first_name"]
            ParentlName = request.POST["parent_last_name"]
            Parentemail = request.POST["parent_email"]
            ParentTele = request.POST["parent_telephone"]
            ParentDOB = request.POST["parent_DOB"]
            ParentSSN = request.POST["parent_SSN"]
        """
        if password == request.POST["Cpassword"]:
            newWebUser = User(first_name=fName, last_name=lName, email=email, password=password)
            return HttpResponseRedirect(reverse("web:login"))
        else:
            return HttpResponseRedirect(request, "extratemplates/register.html", {"error": "Password not matching"})

@login_required(login_url='/login')
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("web:index"))
    

@login_required(login_url='/login')
def account_view(request: HttpRequest):
    try:
        acc = Account.objects.get(user_detail=request.user)
        funds = Fund.objects.all()
    except Account.DoesNotExist:
        return HttpRequest("NO ACCOUNT FOUND")
    organized_shares = []
    if request.method == "GET":
        if request.user == None or type(request.user) == AnonymousUser:
            return HttpResponseRedirect(reverse("web:login"))
        else:
            try:
                for f in funds:
                    shares = Share.objects.filter(owner=acc, fund_of_shares=f)
                    if shares.count() > 0:
                        #l = {f"{f.name}": shares}
                        organized_shares.append(shares)
                    else:
                        continue
                return render(request, "extratemplates/account.html", {"account": acc, "user":request.user, "shares": organized_shares})
            except TypeError:
                return HttpResponseRedirect(reverse("web:login"))

@login_required(login_url='/login')
def marketplace_view(request: HttpRequest):
    shares_for_sale = []
    funds = Fund.objects.all()
    for x in funds:
        shares = Share.objects.filter(fund_of_shares=x, outstanding=True)
        fund_dict = {"fund_id":x.fund_id,"fundName": x.name, "fund_info": x, "sharesForSale": shares, "currentValue": shares[0].current_value, "numberOfShares": shares.count()}
        shares_for_sale.append(fund_dict)
    if request.method == "GET":
        try:
            acc = Account.objects.get(user_detail=request.user)
        except Account.DoesNotExist:
            acc = None
        return render(request, "extratemplates/marketplace.html", {"sharesForSale": shares_for_sale, "account": acc})
    
@login_required(login_url='/login')
def trader_view(request: HttpRequest, fundID: UUID):
    try:
        acc = Account.objects.get(user_detail=request.user)
    except Account.DoesNotExist:
        return HttpRequest("NO ACCOUNT FOUND")
    if request.method == "GET":
        return render(request, "extratemplates/trader.html", {
            "funds":Fund.objects.all(),
            "FundToTrade": Fund.objects.get(fund_id=fundID),
            "account": acc, 
            "user":request.user
        })
    # POST request
    elif request.method == "POST":
        """ 
            1. validate the order (make sure we have enough cash.)
            2. check the shares for a fund and the order type
            3. create a transaction record 
            4. transfer the assets
        """
        tradeType = request.POST["tradeType"]
        fundinTrade = request.POST["fund"]
        numb = int(request.POST["numberOfShares"])
        raw_stocks = Share.objects.filter(fund_of_shares=Fund.objects.get(fund_id=fundID))
        pricePoint = raw_stocks[0].current_value
        print(pricePoint)
        if tradeType == "BUY":
            stocks_for_sale = checkSharesForSale(Fund.objects.get(fund_id=fundID), numb)
            if ((acc.cash_balance < (numb*pricePoint))):
                # cancel transaction, funds are insufficent
                return render(request, "extratemplates/trader.html", {
                    "funds":Fund.objects.all(),
                    "FundToTrade": Fund.objects.get(fund_id=fundID),
                    "account": acc, 
                    "user":request.user,
                    "error": "Error: Insufficent Funds or Volume to Process this Order"
                })
            else:
                process_purchase(acc, Fund.objects.get(fund_id=fundID), numb)
                return render(request, "extratemplates/trader.html", {
                    "funds":Fund.objects.all(),
                    "FundToTrade": Fund.objects.get(fund_id=fundID),
                    "account": acc, 
                    "user":request.user,
                    "error": "Order Processed"
                })
        else:
            return HttpRequest("in progress")


    
    
"""
@login_required(login_url='/login')
def second_factor_login(request):
    info = request.session.get("firstFactor")
    print(info)
    us = User.objects.get(username=info["username"])
    ac = Account.objects.get(user_detail=us)
    if request.method == 'POST':
        try:
            userOTP = OTP.objects.get(user=us, expired=False)
        except OTP.DoesNotExist:
            return render(request, 'web/second_factor_login.html', {"Error": "OTP does not exist with user. "})
        userData = request.POST["OTP-TOKEN"]
        if userOTP.one_time_password == userData:
            # The one-time code is correct, log the user in
            userOTP.expired=True
            userOTP.delete()
            login(request, us)
            return HttpResponseRedirect(reverse("web:account"))  # Redirect to the home page after successful login
    else:
        outstandingOTPs = OTP.objects.filter(user=us)
        outstandingOTPs.delete()
        otp = generate_OTP(ac.account_number)
        OTPClass = OTP(user=us, one_time_password=otp, expired=False)
        OTPClass.save()
        send_otp_email(user=us, otp=OTPClass) 
        return render(request, 'web/second_factor_login.html')
"""