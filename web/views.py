from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from web.models import *
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.decorators import login_required
from django_otp import user_has_device
from django_otp.forms import OTPAuthenticationForm

# Create your views here.
def index(request: HttpRequest):
    return render(request, "web/index.html")

def login_view(request: HttpRequest):
    if request.method == "GET":
        return render(request, "web/login.html")
    else:
        username = request.POST["username"]
        password = request.POST["password"]
        us = User.objects.get(username=username)
        au = authenticate(username=username, password=password)
        if au is not None:
            login(request, au)
            return HttpResponseRedirect(reverse("web:account"))
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
    if not user_has_device(request.user):
        # If the user does not have an OTP device, redirect them to the first-factor login view
        return redirect('first_factor_login')

    if request.method == 'POST':
        form = OTPAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # The one-time code is correct, log the user in
            login(request, form.user)
            return redirect('home')  # Redirect to the home page after successful login
    else:
        form = OTPAuthenticationForm(request)

    return render(request, 'second_factor_login.html', {'form': form})