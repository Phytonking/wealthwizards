from django.contrib import admin
from web.models import *
# Register your models here.


class AccountAdmin(admin.ModelAdmin):
    #list_display = ('share_id')
    search_fields = ('account_number',)

admin.site.register(Account, AccountAdmin)

class FundAdmin(admin.ModelAdmin):
    #list_display = ('share_id')
    search_fields = ('name', 'fund_id')


admin.site.register(Fund, FundAdmin)

class ShareAdmin(admin.ModelAdmin):
    #list_display = ('share_id')
    list_filter = ('sold', 'outstanding')
    search_fields = ('share_id','fund_of_shares')


admin.site.register(Share, ShareAdmin)
admin.site.register(OTP)

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('amount', 'transaction_type', 'timestamp')
    list_filter = ('transaction_type',)
    search_fields = ('amount', 'timestamp')
    
admin.site.register(Transaction, TransactionAdmin)