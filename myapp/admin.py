from django.contrib import admin
from .models import Contact,User,Design,Inquery,Transaction
# Register your models here.

admin.site.register(Contact)
admin.site.register(User)
admin.site.register(Design)
admin.site.register(Inquery)
admin.site.register(Transaction)