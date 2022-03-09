from datetime import datetime
from accounts.models import Managers, Tenants
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import InvalidPage, PageNotAnInteger, Paginator
from django.db.models import Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render)
from rental_property.models import Building, RentalUnit

from utilities_and_rent.filters import (ManagerElectricityBillsFilter,
                                        PaymentsFilter, RentDetailsFilter,
                                        TenantElectricityBillsFilter,
                                        UnitTypeFilter, WaterBilingFilter)
from utilities_and_rent.forms import (AddRentDetailsForm, BillCycleUpdateForm,
                                      ElectricityReadingForm,ElectricityPaySubmitForm, NewElectricityMeterForm, NewWaterMeterForm,
                                      PaymentUpdateForm, StartEBillCycleForm,
                                      StartWaterBillingForm,UpdateElectricityPayForm,
                                      SubmitPaymentsForm, UpdateRentDetails, UpdateWaterPaymentForm,
                                      WaterBillPaymentsForm,
                                      WaterBillUpdateForm, WaterReadingForm)
from utilities_and_rent.models import (ElectricityBilling, ElectricityMeter, ElectricityPayments, ElectricityReadings,
                                       PaymentMethods, RentPayment,
                                       UnitRentDetails, WaterBilling,
                                       WaterConsumption, WaterMeter, WaterPayments)
from config.settings import DEFAULT_FROM_EMAIL
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

User = get_user_model()

current_year = datetime.now().year

@login_required
@user_passes_test(lambda user: user.is_tenant==True, login_url='profile')
def my_rent_details(request, building_slug, unit_slug, username):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(slug=unit_slug, building=building)
    tenant = Tenants.objects.get(rented_unit=unit, associated_account__username=username)
    payment_options = PaymentMethods.objects.all()
    
    tenant_rent_details = UnitRentDetails.objects.filter(tenant=tenant, unit=unit).order_by('-added')
    tenant_rent_details_qs = RentDetailsFilter(request.GET, queryset=tenant_rent_details)
              
    context = {'building':building, 'unit':unit, 'tenant':tenant,'tenant_rent_details_qs':tenant_rent_details_qs,'payment_options':payment_options}
    return render(request, 'utilities_and_rent/my-rent-details.html', context)

@login_required
@user_passes_test(lambda user: user.is_tenant==True, login_url='profile')
def submit_rent_payments(request, building_slug, unit_slug, rent_code, username):
    
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building, slug=unit_slug)
    manager = Managers.objects.get(building_manager__pk=building.id)
    tenant = Tenants.objects.get(rented_unit=unit, associated_account__username=username)
    rent = UnitRentDetails.objects.get(code=rent_code, tenant=tenant)
    previous_payments = RentPayment.objects.filter(tenant=tenant, tenant__rented_unit=unit, rent_details=rent)
    
    if request.method == 'POST':
        pay_info_form = SubmitPaymentsForm(request.POST)
        if pay_info_form.is_valid():
            pay_info_form.instance.rent_details = rent
            pay_info_form.instance.tenant = tenant
            pay_info_form.instance.manager = manager
            pay_info_form.instance.paid_for_month = rent.pay_for_month
            pay_info_form.save()
            messages.success(request, 'Record submitted, update will be done once approved')
            return redirect('my-rent', building_slug=building.slug, unit_slug=unit.slug, username=tenant.associated_account.username)
    else:
        pay_info_form = SubmitPaymentsForm()
        
    context = {'pay_info_form':pay_info_form,'building':building,'rent':rent,
               'tenant':tenant,'unit':unit,'previous_payments':previous_payments}
    return render(request, 'utilities_and_rent/submit-payments-rent.html', context)

@login_required
def my_water_billing(request,building_slug,unit_slug,username):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building,slug=unit_slug)
    tenant = Tenants.objects.get(rented_unit=unit, associated_account__username=username)
    my_water_bills = WaterBilling.objects.filter(rental_unit=unit, tenant=tenant)
    oldest_bill = my_water_bills.exclude(added=None).order_by('-added').last()
    newest_bill = my_water_bills.exclude(added=None).order_by('added').first()
    
    water_bills_qs = WaterBilingFilter(request.GET, queryset=my_water_bills)
    
    context = {'building': building,'unit':unit,'tenant':tenant,'water_bills_qs':water_bills_qs,
               'newest_bill':newest_bill,'oldest_bill':oldest_bill}
    return render(request, 'utilities_and_rent/my_water_bills.html', context)

@login_required
def my_water_billing_details(request,building_slug,unit_slug,username,bill_code):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building,slug=unit_slug)
    tenant = Tenants.objects.get(rented_unit=unit, associated_account__username=username)
    water_bill = WaterBilling.objects.get(rental_unit=unit,tenant=tenant,bill_code=bill_code)
    child_readings = WaterConsumption.objects.filter(parent=water_bill)
    payments_made = WaterPayments.objects.filter(parent=water_bill)
    
    if request.method == 'POST':
        bill_pay_form = WaterBillPaymentsForm(request.POST)
        if bill_pay_form.is_valid():
            bill_pay_form.instance.parent = water_bill
            bill_pay_form.save()
            messages.success(request, 'Payment submitted')
            return HttpResponseRedirect("")
    else:
        bill_pay_form = WaterBillPaymentsForm()
    context = {'building':building,'unit':unit,'tenant':tenant,'water_bill':water_bill,
               'bill_pay_form':bill_pay_form,'child_readings':child_readings,'payments_made':payments_made}
    return render(request, 'utilities_and_rent/my_water_bill_details.html', context)

@login_required
def my_electric_bills(request, building_slug, unit_slug, username):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building,slug=unit_slug)
    tenant = Tenants.objects.get(rented_unit=unit,associated_account__username=username)
    e_bills = ElectricityBilling.objects.filter(rental_unit=unit,tenant=tenant).order_by('added')
    
    e_bills_qs = TenantElectricityBillsFilter(request.GET, queryset=e_bills)
    oldest_bill = e_bills.exclude(added=None).order_by('-added').last()
    newest_bill = e_bills.exclude(added=None).order_by('added').first()
    
    context = {'building':building,'unit':unit,'tenant':tenant,'e_bills':e_bills_qs,
               'oldest_bill':oldest_bill,'newest_bill':newest_bill}
    return render(request, 'utilities_and_rent/my_e_bills.html', context)

@login_required
def my_electricity_billing_details(request,building_slug,unit_slug,username,bill_code):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building,slug=unit_slug)
    tenant = Tenants.objects.get(rented_unit=unit, associated_account__username=username)
    e_bill = ElectricityBilling.objects.get(rental_unit=unit,tenant=tenant,bill_code=bill_code)
    readings = ElectricityReadings.objects.filter(parent=e_bill)
    payments_made = ElectricityPayments.objects.filter(parent=e_bill)
    
    if request.method == 'POST':
        pay_submit_form = ElectricityPaySubmitForm(request.POST)
        if pay_submit_form.is_valid():
            pay_submit_form.instance.parent = e_bill
            pay_submit_form.save()
            messages.success(request, 'Your record has been subitted')
            return HttpResponseRedirect("")
    else:
        pay_submit_form = ElectricityPaySubmitForm()
        
    context = {'building':building,'unit':unit,'tenant':tenant,'e_bill':e_bill,
               'readings':readings,'pay_submit_form':pay_submit_form,'payments_made':payments_made}
    return render(request, 'utilities_and_rent/my_elctric_bill_details.html', context)


############### manager functions ###################

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def rent_and_utilities(request, building_slug):
    building = Building.objects.get(slug=building_slug)
    tenants = Tenants.objects.filter(rented_unit__building=building)
    tenants_filter = UnitTypeFilter(request.GET, queryset=tenants)
    
    if request.method == 'POST':
        water_meter_add_form = NewWaterMeterForm(building, request.POST)
        electricity_meter_add_form = NewElectricityMeterForm(building, request.POST)
        if water_meter_add_form.is_valid():
            water_meter_add_form.save()
            messages.success(request, 'Water meter added')
            return HttpResponseRedirect("")
        if electricity_meter_add_form.is_valid():
            electricity_meter_add_form.save()
            messages.success(request, 'Electricity meter added')
            return HttpResponseRedirect("")
    else:
        water_meter_add_form = NewWaterMeterForm(building)
        electricity_meter_add_form = NewElectricityMeterForm(building)
    
    context = {'building':building, 'tenants_filter':tenants_filter,'current_year':current_year,
               'water_meter_add_form':water_meter_add_form,'electricity_meter_add_form':electricity_meter_add_form,}
    return render(request, 'utilities_and_rent/building_utility_and_rent.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def tenant_rent_history(request, building_slug, unit_slug, username):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(slug=unit_slug, building=building)
    tenant = Tenants.objects.get(rented_unit=unit, associated_account__username=username)
    rent_details = UnitRentDetails.objects.filter(tenant=tenant, unit=unit).order_by('-added')
    rental_details_filter = RentDetailsFilter(request.GET, queryset=rent_details)
    
    context = {'building': building,'unit':unit,
               'tenant':tenant,'rent_details':rental_details_filter}
    return render(request, 'utilities_and_rent/tenant-rent-history.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def add_tenant_rent(request, building_slug, unit_slug):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building, slug=unit_slug)
    
    if unit.status == 'occupied':
        tenant = Tenants.objects.get(rented_unit=unit)
        if request.method == 'POST':
            rent_form = AddRentDetailsForm(request.POST)
            if rent_form.is_valid():
                rent_form.instance.tenant = tenant
                rent_form.instance.unit = unit
                rent_form.save()
                messages.success(request, 'Rent added successfully')
                notify = rent_form.instance
                if notify.notify_tenant == True:
                    subject = "Rent Added For '{0} {1}'".format(notify.pay_for_month, current_year)
                    notify_content = 'utilities_and_rent/mails/notify_rent.html'
                    html_message = render_to_string(notify_content, 
                                                    {'building':building,'notify':notify,'current_year':current_year,})
                    from_email = DEFAULT_FROM_EMAIL
                    to_email = tenant.associated_account.email
                    message = EmailMessage(subject, html_message, from_email, [to_email])
                    message.content_subtype = 'html'
                    message.send()
                    messages.info(request,'Notification sent')
                return redirect('rent-history', building_slug=building.slug, unit_slug=unit.slug, username=tenant.associated_account.username)
        else:
            rent_form = AddRentDetailsForm()
    else:
        messages.success(request, 'The rental unit is empty')
        return redirect('rent-and-utilities', building_slug=building.slug)
    context = {'rent_form':rent_form, 'building':building, 'unit':unit,'tenant':tenant}
    return render(request, 'utilities_and_rent/add-rent.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def update_tenant_rent(request, building_slug, unit_slug, username, rent_code):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building,slug=unit_slug)
    tenant = Tenants.objects.get(rented_unit=unit, associated_account__username=username)
    rent_details = UnitRentDetails.objects.get(tenant=tenant, code=rent_code)
    
    if request.method == 'POST':
        update_form = UpdateRentDetails(request.POST, instance=rent_details)
        if update_form.is_valid():
            update_form.save()
            messages.success(request, 'Rent updated successfully')
            notify = update_form.instance
            if notify.notify_tenant == True:
                subject = "Rent Adjustment for '{0} {1}'".format(notify.pay_for_month, current_year)
                notify_content = 'utilities_and_rent/mails/notify_rent.html'
                html_message = render_to_string(notify_content,
                                                {'building':building,'notify':notify,'current_year':current_year,})
                from_email = DEFAULT_FROM_EMAIL
                to_email = tenant.associated_account.email
                message = EmailMessage(subject, html_message, from_email, [to_email])
                message.content_subtype = 'html'
                message.send()
                messages.info(request,'Tenant Notified')
            return redirect('rent-history', building_slug=building.slug, unit_slug=unit.slug, username=tenant.associated_account.username)
    else:
        update_form = UpdateRentDetails(instance=rent_details)
    
    payments = RentPayment.objects.filter(rent_details=rent_details)
    payment_filter = PaymentsFilter(request.GET, queryset=payments)
    
    context = {'update_form':update_form,'building':building,'unit':unit,'tenant':tenant,'rent_details':rent_details,
               'payments':payment_filter,}
    return render(request, 'utilities_and_rent/manager-update-view-payments.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def update_tenant_rent_payment(request, building_slug, unit_slug, username, rent_code, track_code):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building,slug=unit_slug)
    tenant = Tenants.objects.get(rented_unit=unit, associated_account__username=username)
    parent_rent =  UnitRentDetails.objects.get(tenant=tenant, code=rent_code)
    payment = RentPayment.objects.get(rent_details=parent_rent, tracking_code=track_code)
    
    if request.method == 'POST':
        pay_update_form = PaymentUpdateForm(request.POST, instance=payment)
        if pay_update_form.is_valid():
            pay_update_form.save()
            if pay_update_form.instance.status=='approved':
                update_rent = parent_rent
                update_rent.amount_paid += pay_update_form.instance.amount
                update_rent.save()
                messages.success(request, 'Payment updated successfully')
                notify = pay_update_form.instance
                if notify.status == 'approved' and notify.notify_tenant == True:
                    subject = "Rent Payment Status '{0}'".format(notify.status)
                    notify_content = 'utilities_and_rent/mails/notify_rent_payment.html'
                    html_message = render_to_string(notify_content,
                                                {'building':building,'notify':notify,})
                    from_email = DEFAULT_FROM_EMAIL
                    to_email = tenant.associated_account.email
                    message = EmailMessage(subject, html_message, from_email, [to_email])
                    message.content_subtype = 'html'
                    message.send()
                    messages.info(request,'Tenant notification sent')
            return HttpResponseRedirect("")
    else:
        pay_update_form = PaymentUpdateForm(instance=payment)
    
    context = {'building': building,'unit':unit,'tenant':tenant,'pay_update_form':pay_update_form,
               'parent_rent':parent_rent,'payment':payment}
    return render(request, 'utilities_and_rent/rent-payment-update.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def manage_tenant_water_billing(request, building_slug, unit_slug, username):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building,slug=unit_slug)
    tenant = Tenants.objects.get(rented_unit=unit,associated_account__username=username)
    water_billing_set = WaterBilling.objects.filter(rental_unit=unit,tenant=tenant)
    billing_queryset = WaterBilingFilter(request.GET, queryset=water_billing_set)
    check_open_billing = WaterBilling.objects.filter(rental_unit=unit,tenant=tenant,lock_cycle=False)
    oldest_bill = water_billing_set.exclude(added=None).order_by('-added').last()
    newest_bill = water_billing_set.exclude(added=None).order_by('added').first()
    
    check_water_meter = WaterMeter.objects.filter(unit=unit)
    if check_water_meter:
        water_meter = WaterMeter.objects.get(unit=unit)
        if request.method == 'POST':
            add_bill_form = StartWaterBillingForm(request.POST)
            if add_bill_form.is_valid():
                add_bill_form.instance.tenant = tenant
                add_bill_form.instance.rental_unit = unit
                add_bill_form.instance.meter_number = water_meter
                add_bill_form.save()
                messages.success(request, 'Billing started, you can add readings now')
                return HttpResponseRedirect("")
        else:
            add_bill_form = StartWaterBillingForm()
    else:
        messages.info(request, 'No available water meter available for the unit, please add one first')
        return redirect("rent-and-utilities", building_slug=building.slug)
    
    context = {
        'building':building,'unit':unit,'tenant':tenant,'water_billing_set':billing_queryset,'check_open_billing':check_open_billing,
        'oldest_bill':oldest_bill,'newest_bill':newest_bill,'add_bill_form':add_bill_form,'water_meter':water_meter}
    return render(request, 'utilities_and_rent/manager-water-billing.html', context)


@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def update_tenant_water_billing_details(request, building_slug, unit_slug, username, bill_code):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building,slug=unit_slug)
    tenant = Tenants.objects.get(rented_unit=unit,associated_account__username=username)
    bill_cycle = WaterBilling.objects.get(rental_unit=unit,tenant=tenant,bill_code=bill_code)
    readings = WaterConsumption.objects.filter(parent=bill_cycle)
    water_bill_payments = WaterPayments.objects.filter(parent=bill_cycle)
    
    if request.method == 'POST':
        update_bill_form = WaterBillUpdateForm(request.POST, instance=bill_cycle)
        reading_form = WaterReadingForm(request.POST)
        if update_bill_form.is_valid():
            update_bill_form.save()
            messages.success(request, 'Water billing updated successfully!')
            return HttpResponseRedirect("")
        if reading_form.is_valid():
            reading_form.instance.parent = bill_cycle
            reading_form.save()
            bill_update = bill_cycle
            bill_update.units += reading_form.instance.consumption 
            bill_update.save(update_fields=['units','total'])
            messages.success(request, 'Reading added successfully!')
            return HttpResponseRedirect("")
    else:
        reading_form = WaterReadingForm()
        update_bill_form = WaterBillUpdateForm(instance=bill_cycle)
        
    context = {'update_bill_form':update_bill_form,'reading_form':reading_form,'building':building,
               'unit':unit,'tenant':tenant,'bill_cycle':bill_cycle,'readings':readings,'water_bill_payments':water_bill_payments}
    return render(request, 'utilities_and_rent/tenant-water-billing-details.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def update_water_payments(request,building_slug,unit_slug,username,bill_code,tracking_code):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building,slug=unit_slug)
    tenant = Tenants.objects.get(rented_unit=unit,associated_account__username=username)
    water_bill = WaterBilling.objects.get(rental_unit=unit,tenant=tenant,bill_code=bill_code)
    pay_to_update = WaterPayments.objects.get(parent=water_bill,tracking_code=tracking_code)
    
    if pay_to_update.lock:
        messages.error(request, 'This instance is locked, updates not allowed')
        return redirect('update_tenant_water_billing_details', building_slug=building.slug,unit_slug=unit.slug,
                            username=tenant.associated_account.username,bill_code=water_bill.bill_code)
    else:
        if request.method == 'POST':
            update_form = UpdateWaterPaymentForm(request.POST, instance=pay_to_update)
            if update_form.is_valid():
                update_form.save()
                messages.success(request, 'Record updated')
                updater = update_form.instance
                if updater.status == 'approved':
                    bill = water_bill
                    bill.amount_paid += updater.amount
                    bill.save()
                    messages.success(request, 'Water bill updated')
                return redirect('update_tenant_water_billing_details', building_slug=building.slug,unit_slug=unit.slug,
                            username=tenant.associated_account.username,bill_code=water_bill.bill_code)
        else:
            update_form = UpdateWaterPaymentForm(instance=pay_to_update)
    context = {'form': update_form}
    return render(request, 'utilities_and_rent/update_waterbill_pay.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def manage_tenant_electric_bills(request, building_slug, unit_slug, username):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building,slug=unit_slug)
    tenant = Tenants.objects.get(rented_unit=unit,associated_account__username=username)
    related_bills = ElectricityBilling.objects.filter(rental_unit=unit,tenant=tenant).order_by('added')
    
    bills_qs = ManagerElectricityBillsFilter(request.GET, queryset=related_bills)

    check_open_billing = ElectricityBilling.objects.filter(rental_unit=unit,tenant=tenant,lock_cycle=False)
    
    check_available_meter = ElectricityMeter.objects.filter(unit=unit)
    if check_available_meter:
        electricity_meter = ElectricityMeter.objects.get(unit=unit)
        if request.method == 'POST':
            start_e_bill_cycle_form = StartEBillCycleForm(request.POST)
            if start_e_bill_cycle_form.is_valid():
                start_e_bill_cycle_form.instance.tenant = tenant
                start_e_bill_cycle_form.instance.rental_unit = unit
                start_e_bill_cycle_form.instance.meter_id = electricity_meter
                start_e_bill_cycle_form.save()
                messages.success(request, "Successfully started new billing")
                return HttpResponseRedirect("")
        else:
            start_e_bill_cycle_form = StartEBillCycleForm()
    else:
        messages.info(request, 'Electricity meter not found, please add one for the unit first')
        return redirect("rent-and-utilities", building_slug=building.slug)
    
    context = {'building':building,'unit':unit,'tenant':tenant,'bills':bills_qs,'electricity_meter':electricity_meter,
               'bill_form':start_e_bill_cycle_form,'check_open_billing':check_open_billing}
    return render(request, 'utilities_and_rent/tenant_electricity_bills.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def update_tenant_electric_bill_details(request,building_slug,unit_slug,username,bill_code):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building,slug=unit_slug)
    tenant = Tenants.objects.get(rented_unit=unit,associated_account__username=username)
    e_bill = ElectricityBilling.objects.get(rental_unit=unit,tenant=tenant,bill_code=bill_code)
    added_readings = ElectricityReadings.objects.filter(parent=e_bill)
    electricity_payments = ElectricityPayments.objects.filter(parent=e_bill)
    
    if request.method == 'POST':
        update_bill_form = BillCycleUpdateForm(request.POST, instance=e_bill)
        reading_form = ElectricityReadingForm(request.POST)
        if update_bill_form.is_valid():
            update_bill_form.save()
            messages.success(request, 'Cycle updated successfully!')
            return HttpResponseRedirect("")
        if reading_form.is_valid():
            reading_form.instance.parent = e_bill
            reading_form.instance.units = reading_form.instance.current_reading-reading_form.instance.previous_reading
            reading_form.save()
            send_update = e_bill
            send_update.units += reading_form.instance.units
            send_update.save(update_fields=['units','total'])
            messages.success(request, 'Reading adde successfully!')
            return HttpResponseRedirect("")
    else:
        reading_form = ElectricityReadingForm()
        update_bill_form = BillCycleUpdateForm(instance=e_bill)
    
    context = {'building':building, 'unit':unit,'tenant':tenant,'e_bill':e_bill,'added_readings':added_readings,
               'update_bill_form':update_bill_form,'reading_form':reading_form,'electricity_payments':electricity_payments,}
    return render(request, 'utilities_and_rent/tenant_electricity_bill_details.html', context)

@login_required
@user_passes_test(lambda user: user.is_manager==True, login_url='profile')
def update_electricity_payments(request,building_slug,unit_slug,username,bill_code,t_code):
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building,slug=unit_slug)
    tenant = Tenants.objects.get(rented_unit=unit,associated_account__username=username)
    e_bill = ElectricityBilling.objects.get(rental_unit=unit,tenant=tenant,bill_code=bill_code)
    pay_to_update = ElectricityPayments.objects.get(parent=e_bill,tracking_code=t_code)
    
    if pay_to_update.lock:
        messages.error(request, 'Further updates not allowed!')
        return redirect('tenant_electric_bill_details', building_slug=building.slug,unit_slug=unit.slug,
                            username=tenant.associated_account.username,bill_code=e_bill.bill_code)
    else:
        if request.method == 'POST':
            update_form = UpdateElectricityPayForm(request.POST, instance=pay_to_update)
            if update_form.is_valid():
                update_form.save()
                messages.success(request, 'Record updated')
                updater = update_form.instance
                if updater.status == 'approved':
                    bill = e_bill
                    bill.amount_paid += updater.amount
                    bill.save()
                    messages.success(request, 'Electricity bill updated')
                return redirect('tenant_electric_bill_details', building_slug=building.slug,unit_slug=unit.slug,
                            username=tenant.associated_account.username,bill_code=e_bill.bill_code)
        else:
            update_form = UpdateElectricityPayForm(instance=pay_to_update)
            
    context = {'form': update_form}
    return render(request, 'utilities_and_rent/update_electricity_pay.html', context)
    
########## Graphs #############

@login_required
def rent_chart(request,building_slug,unit_slug,username):
    labels = []
    data = []
    
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building,slug=unit_slug)
    tenant = Tenants.objects.get(rented_unit=unit,associated_account__username=username)
    
    queryset = UnitRentDetails.objects.filter(tenant=tenant,unit=unit).values(
        'pay_for_month').annotate(rent_amount=Sum('rent_amount')).order_by('added')[:6]
    
    for entry in queryset:
        labels.append(entry['pay_for_month'])
        data.append(entry['rent_amount'])
    
    data = {
        'labels': labels,
        'data': data,
    }
    return JsonResponse(data)

@login_required
def tenant_water_usage(request,building_slug,unit_slug,username):
    labels = []
    data = []
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building,slug=unit_slug)
    tenant = Tenants.objects.get(rented_unit=unit,associated_account__username=username)
    queryset = WaterConsumption.objects.filter(
        parent__rental_unit=unit,parent__tenant=tenant).values('reading_added').annotate(
            consumption=Sum('consumption')).order_by('reading_added')[:10] #last 10 readings
    
    for entry in queryset:
        labels.append(entry['reading_added'])
        data.append(entry['consumption'])
    
    data = {'labels':labels,'data':data}
    return JsonResponse(data)

@login_required
def tenant_electricity_usage(request,building_slug,unit_slug,username):
    labels = []
    data = []
    building = Building.objects.get(slug=building_slug)
    unit = RentalUnit.objects.get(building=building,slug=unit_slug)
    tenant = Tenants.objects.get(rented_unit=unit,associated_account__username=username)
    queryset = ElectricityReadings.objects.filter(
        parent__rental_unit=unit,parent__tenant=tenant).values('reading_date').annotate(
            units=Sum('units')).order_by('reading_date')[:10] #last 10 readings
    
    for entry in queryset:
        labels.append(entry['reading_date'])
        data.append(entry['units'])
    
    data = {'labels':labels,'data':data}
    return JsonResponse(data)

@login_required
def building_rent_overview(request,building_slug):
    building = Building.objects.get(slug=building_slug)
    
    data = []
    labels = []
    
    current_year = datetime.now().year
        
    queryset = UnitRentDetails.objects.filter(unit__building=building,added__year=current_year
                                              ).values('pay_for_month').annotate(
                                                  amount=Sum('rent_amount'))
                                              
    for entry in queryset:
        labels.append(entry['pay_for_month'])
        data.append(entry['amount'])
    
    data = {'labels': labels,'data': data}
    return JsonResponse(data)