from django.contrib import admin
from Company.models import company
# Register your models here.
class AdminCompany(admin.ModelAdmin) :
    list_display = ()

admin.site.register(Company, AdminCompany)