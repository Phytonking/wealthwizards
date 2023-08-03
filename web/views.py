from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from web.models import *
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.decorators import login_required
from django_otp import user_has_device
from web.tools import *

# Create your views here.
def index(request: HttpRequest):
    return render(request, "web/index.html")

def login_view(request: HttpRequest):
    if request.method == "GET":
        return render(request, "web/login.html")
    else:
        username = request.POST["username"]
        password = request.POST["password"]
        try:
            us = User.objects.get(username=username)
        except User.DoesNotExist:
            return render(request, "web/login.html", {"error": "User does not exist"})
        au = authenticate(username=username, password=password)
        if au is not None:
            request.session['firstFactor'] = request.POST
            return HttpResponseRedirect(reverse("web:second_factor_login"))
        else:
            return render(request, "web/login.html", {"error": "Incorrect Username or Password"})
        

def register_view(request: HttpRequest):
    return render(request, "web/register.html")

@login_required(login_url='/login')
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("web:index"))

@login_required(login_url='/login')
def account_view(request: HttpRequest):
    acc = Account.objects.get(user_detail=request.user)
    funds = Fund.objects.all()
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
                return render(request, "web/account.html", {"account": acc, "user":request.user, "shares": organized_shares})
            except TypeError:
                return HttpResponseRedirect(reverse("web:login"))

@login_required(login_url='/login')
def marketplace_view(request: HttpRequest):
    shares_for_sale = []
    funds = Fund.objects.all()
    for x in funds:
        shares = Share.objects.filter(fund_of_shares=x, outstanding=True)
        fund_dict = {"fundName": x.name, "fund_info": x, "sharesForSale": shares, "currentValue": shares[0].current_value, "numberOfShares": shares.count()}
        shares_for_sale.append(fund_dict)
    if request.method == "GET":
        acc = Account.objects.get(user_detail=request.user)
        return render(request, "web/marketplace.html", {"sharesForSale": shares_for_sale, "account": acc})
    
@login_required(login_url='/login')
def trader_view(request: HttpRequest):
    if request.method == "GET":
        return render(request, "web/trader.html")
    


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