from django.urls import path
from utilities_and_rent import views

urlpatterns = [
    path('my-rent/<slug:building_slug>/<slug:unit_slug>/<slug:username>/', views.my_rent_details, name='my-rent'),
    path('submit-rent-pay-info/<slug:building_slug>/<slug:unit_slug>/<slug:rent_code>/<slug:username>/', views.submit_rent_payments, name='pay-info'),
    path('rent-and-utilities/<slug:building_slug>/', views.rent_and_utilities, name='rent-and-utilities'),
    path('add-rent/<slug:building_slug>/<slug:unit_slug>/', views.add_tenant_rent, name='add-rent'),
    path('my_water_billing/<slug:building_slug>/<slug:unit_slug>/<slug:username>/', views.my_water_billing, name='my_water_billing'),
    path('my_water_billing_details/<slug:building_slug>/<slug:unit_slug>/<slug:username>/<slug:bill_code>/', views.my_water_billing_details, name="my_water_billing_details"),
    path('rent-history/<slug:building_slug>/<slug:unit_slug>/<slug:username>/', views.unit_rent_history, name='rent-history'),
    path('tenant-rent-update-view/<slug:building_slug>/<slug:unit_slug>/<slug:username>/<slug:rent_code>/', views.update_tenant_rent, name='view-update-rent'),
    path('update-payment/<slug:building_slug>/<slug:unit_slug>/<slug:username>/<slug:rent_code>/<slug:track_code>/', views.update_tenant_rent_payment, name='update-rent'),
    path('rent-chart/<slug:building_slug>/<slug:unit_slug>/<slug:username>/', views.rent_chart, name='rent_chart'),
    path('water-usage/<slug:building_slug>/<slug:unit_slug>/<slug:username>/', views.tenant_water_usage, name='tenant-water-usage'),
    path('water-billing/<slug:building_slug>/<slug:unit_slug>/<slug:username>/', views.manage_tenant_water_billing, name='manager-water-billing'),
    path('water-bill-detail/<slug:building_slug>/<slug:unit_slug>/<slug:username>/<slug:bill_code>/', views.update_tenant_water_billing_details, name="water-billing-details"),
]