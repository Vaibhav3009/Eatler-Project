from django.contrib import admin
from . import models
# Register your models here.


class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ('order_date','order_time')

admin.site.register(models.Product)
admin.site.register(models.Restaurant)
admin.site.register(models.Order,OrderAdmin)
admin.site.register(models.Address)
admin.site.register(models.Issues)
admin.site.register(models.UserInfo)
admin.site.register(models.BookTable)
admin.site.register(models.Feedback)