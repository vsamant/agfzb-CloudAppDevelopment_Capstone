from django.contrib import admin
from .models import CarMake, CarModel

# Register your models here.

# CarModelInline class
class CarModelInline(admin.StackedInline):
    model = CarModel
    extra = 2

# CarModelAdmin class
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_type', 'year')
    list_filter = ['model_type', 'year']
    search_fields = ['model_type']

# CarMakeAdmin class with CarModelInline
class CarMakeAdmin(admin.ModelAdmin):
    inlines = [CarModelInline]
    list_filter = ['name']
    search_fields = ['name']


# Register models here
admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel, CarModelAdmin)