from django.forms import inlineformset_factory

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from .forms import VendorDetailForm,categoryForm,CustomerDetailForm,companyForm,ItemDetailForm,StoreDetailForm,Bag_BoxesDetailForm,BillOfMaterialsForm
from .models import VendorDetail,category,CustomerDetail,company,ItemDetail,StoreDetail,Bag_BoxesDetails,BillOfMaterials
from django.http import JsonResponse
import json
from django.db import connection 
from Administrator_settings.models import User
from django.contrib import messages

from django.contrib.auth import logout
from django.shortcuts import redirect,render

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')  # Redirect after logout
    return redirect('login')  # Fallback redirect

def login_view(request):
    users = User.objects.all()
    """Handle user login."""
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')

        try:
            user = User.objects.get(name=name, password=password)
            request.session['user_id'] = user.id
            request.session['username'] = user.name
            request.session['location'] = user.location
            return redirect('home')
        except User.DoesNotExist:
            error_message = "Invalid username or password. Please try again."
            return render(request, 'master/login.html', {'users': users, 'error_message': error_message})

    return render(request, 'master/login.html', {'users': users})


def forgot_password_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        new_password = request.POST.get('new_password')

        try:
            user = User.objects.get(name=name)
            user.password = new_password  # (In production, use hashing)
            user.save()
            messages.success(request, 'Password reset successfully.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')

    return render(request, 'master/forgot_password.html')

from django.shortcuts import render
from django.db.models import Sum, Value, DecimalField, Q
from django.db.models.functions import Coalesce
from decimal import Decimal, InvalidOperation

from master.models import ItemDetail, BillOfMaterials
from raw_material.models import RawInwardMaterialSub, RmMaterialIssueSub
from finished_goods.models import FGInwardMaterialSub, PackingSlipItem
from packing_materials.models import PackingInwardMaterialSub, pmmaterialissuesub

def home_view(request):
    stock_chart_data = []

    inward_items = ItemDetail.objects.filter(
        Q(item_code__in=RawInwardMaterialSub.objects.values('item_code')) |
        Q(item_code__in=FGInwardMaterialSub.objects.values('item_code')) |
        Q(item_code__in=PackingInwardMaterialSub.objects.values('item_code'))
    ).distinct()

    for item in inward_items:
        item_code = item.item_code
        item_name = item.item_name
        category = item.category.name if item.category else "Unknown"

        inward_raw = RawInwardMaterialSub.objects.filter(item_code=item_code).aggregate(
            total=Coalesce(Sum('quantity'), Value(0, output_field=DecimalField()))
        )['total']
        inward_fg = FGInwardMaterialSub.objects.filter(item_code=item_code).aggregate(
            total=Coalesce(Sum('quantity'), Value(0, output_field=DecimalField()))
        )['total']
        inward_pm = PackingInwardMaterialSub.objects.filter(item_code=item_code).aggregate(
            total=Coalesce(Sum('quantity'), Value(0, output_field=DecimalField()))
        )['total']

        total_inward_stock = inward_raw + inward_fg + inward_pm

        issued_rm = RmMaterialIssueSub.objects.filter(item_code=item_code).aggregate(
            total=Coalesce(Sum('quantity'), Value(0, output_field=DecimalField()))
        )['total']
        issued_fg = PackingSlipItem.objects.filter(item_code=item_code).aggregate(
    total=Coalesce(Sum('qty', output_field=DecimalField()), Value(0, output_field=DecimalField()))
)['total']

        issued_pm = pmmaterialissuesub.objects.filter(item_code=item_code).aggregate(
    total=Coalesce(Sum('quantity', output_field=DecimalField()), Value(0, output_field=DecimalField()))
)['total']

        bom_rm_deduction = Decimal(0)
        bom_pm_deduction = Decimal(0)

        bom_fg_entries = BillOfMaterials.objects.filter(item_code=item_code)
        for bom in bom_fg_entries:
            try:
                required_qty = Decimal(bom.required_qty)
            except (TypeError, ValueError, InvalidOperation):
                required_qty = Decimal(0)

            fg_produced_qty = FGInwardMaterialSub.objects.filter(item_code=bom.item.item_code).aggregate(
                total=Coalesce(Sum('quantity'), Value(0, output_field=DecimalField()))
            )['total']

            deduction = required_qty * fg_produced_qty

            if category == "Raw Material":
                bom_rm_deduction += deduction
            elif category == "Packing Material":
                bom_pm_deduction += deduction

        total_issued_stock = issued_rm + issued_fg + issued_pm + bom_rm_deduction + bom_pm_deduction
        closing_stock = total_inward_stock - total_issued_stock
        opening_stock = total_inward_stock - total_issued_stock

        rate = item.rate if item.rate else Decimal(0)

        stock_chart_data.append({
            'item_name': item_name,
            'category': category,
            'opening': float(opening_stock),
            'closing': float(closing_stock),
            'rate': float(rate)
        })

    return render(request, 'master/home.html', {
        'stock_chart_data': stock_chart_data
    })


def vendor_list(request):
    """Display all vendors with options to add, edit, and delete."""
    vendors = VendorDetail.objects.all()
    return render(request, 'master/vendor_list.html', {'vendors': vendors})

def vendor_add(request):
    """Add a new vendor."""
    if request.method == 'POST':
        form = VendorDetailForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vendor_list')
    else:
        form = VendorDetailForm()

    return render(request, 'master/vendor_form.html', {'form': form, 'title': 'Add Vendor', "hide_logout": True})

def vendor_edit(request, pk):
    """Edit an existing vendor."""
    vendor = get_object_or_404(VendorDetail, pk=pk)
    if request.method == 'POST':
        form = VendorDetailForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            return redirect('vendor_list')
    else:
        form = VendorDetailForm(instance=vendor)

    return render(request, 'master/vendor_form.html', {'form': form, 'title': 'Edit Vendor', "hide_logout": True})

def vendor_delete(request, pk):
    """Delete a vendor."""
    vendor = get_object_or_404(VendorDetail, pk=pk)
    if request.method == 'POST':
        vendor.delete()
        return redirect('vendor_list')
    
    return render(request, 'master/vendor_form.html', {'vendor': vendor})

def vendor_detail(request, pk):
    """Display a Vendor in view-only mode."""
    vendor = get_object_or_404(VendorDetail, pk=pk)
    form = VendorDetailForm(instance=vendor)

    # Render vendor form in view-only mode
    return render(request, 'master/vendor_form.html', {
        'form': form,
        'title': 'View Vendor',
        'view_mode': True,  # View mode enabled
        'hide_logout': True,  # Optional: Hide logout if necessary
    })







def category_list(request):
    """Display all categories with options to add, edit, and delete."""
    categories = category.objects.all()
    return render(request, 'master/category_list.html', {'categories': categories})

def category_add(request):
   
   
    if request.method == 'POST':
        form = categoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = categoryForm()

    return render(request, 'master/category_form.html', {'form': form, 'title': 'Add Category', "hide_logout": True})

def category_edit(request, pk):
   
    category_instance = get_object_or_404(category, pk=pk)
    if request.method == 'POST':
        form = categoryForm(request.POST, instance=category_instance)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = categoryForm(instance=category_instance)

    return render(request, 'master/category_form.html', {'form': form, 'title': 'Edit Category', "hide_logout": True})

def category_delete(request, pk):
    """Delete a category."""
    category_instance = get_object_or_404(category, pk=pk)
    if request.method == 'POST':
        category_instance.delete()
        return redirect('category_list')

    return render(request, 'master/category_confirm_delete.html', {'category': category_instance})

def category_detail(request, pk):
   
    category_instance = get_object_or_404(category, pk=pk)
    form = categoryForm(instance=category_instance)

    return render(request, 'master/category_form.html', {'form': form, 'title': 'View Category', 'view_mode': True, "hide_logout": True})



def customer_list(request):

    """Display all customers with options to add, edit, and delete."""

    customers = CustomerDetail.objects.all()

    return render(request, 'master/customer_list.html', {'customers': customers})

def customer_view(request, pk):
    """Display a Customer in view-only mode."""
    # Fetch all traders using raw SQL
    with connection.cursor() as cursor:
        cursor.execute("SELECT tradersid, tradersname FROM traders")
        traders_list = cursor.fetchall()

    # Convert list of tuples to a list of dictionaries
    traders_list = [{'id': row[0], 'name': row[1]} for row in traders_list]

    # Get the selected customer details
    customer = get_object_or_404(CustomerDetail, pk=pk)

    # Populate form with customer details in view mode
    form = CustomerDetailForm(instance=customer)

    return render(request, 'master/customer_detail_form.html', {
        'form': form,
        'title': 'View Customer',
        'view_mode': True,  # Ensures fields are disabled
        'hide_logout': True,  # Hide logout if necessary
        'traders': traders_list
    })


def customer_add(request):
    """Add a new customer."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT tradersid, tradersname FROM traders")
        traders_list = cursor.fetchall()

    traders_list = [{'id': row[0], 'name': row[1]} for row in traders_list]

    if request.method == 'POST':
        form = CustomerDetailForm(request.POST)
        print("Form Data:", request.POST)
        print("Form Errors:", form.errors)

        if form.is_valid():
            customer = form.save(commit=False)
            customer.active = request.POST.get('active') == 'on'
            customer.save()
            return redirect('customer_list')
    else:
        form = CustomerDetailForm(initial={'active': False})

    return render(request, 'master/customer_detail_form.html', {
        'form': form,
        'title': 'Add Customer',
        'hide_logout': True,
        'traders': traders_list
    })



def customer_edit(request, pk):
    """Edit an existing customer."""
    with connection.cursor() as cursor:
      cursor.execute("SELECT tradersid, tradersname FROM traders")
      traders_list = cursor.fetchall()  # Fetch all traders from DB

  # Convert list of tuples to a list of dictionaries
    traders_list = [{'id': row[0], 'name': row[1]} for row in traders_list]
    customer = get_object_or_404(CustomerDetail, pk=pk)

    if request.method == 'POST':
        form = CustomerDetailForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save(commit=False)

            # ✅ Handle Active/Inactive properly
            customer.active = request.POST.get('active') == 'on'

            customer.save()
            return redirect('customer_list')
    else:
        form = CustomerDetailForm(instance=customer)

    return render(request, 'master/customer_detail_form.html', {'form': form, 'title': 'Edit Customer',"hide_logout": True, "hide_logout": True,'traders': traders_list,})

 
 
def customer_delete(request, pk):

    """Delete a customer."""

    customer = get_object_or_404(CustomerDetail, pk=pk)

    if request.method == 'POST':

        customer.delete()

        return redirect('customer_list')

    return render(request, 'customer_detail_form.html', {'customer_name': customer})

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # if not using @csrf_exempt, make sure CSRF token is passed correctly
def company_form(request):
    if request.method == 'POST':
        form = companyForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True, "message": "Company details saved"})
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
    else:
        form = companyForm()
    return render(request, 'master/company_form.html', {"form": form})

def item_list(request):
    """Display all items with options to add, edit, and delete."""
    item_master = ItemDetail.objects.all()
    return render(request, 'master/item_list.html', {'item_master': item_master})
 
def item_add(request):
    """Add a new Item with BOM details."""
    BOMFormSet = inlineformset_factory(
        ItemDetail, BillOfMaterials, form=BillOfMaterialsForm, extra=1, can_delete=True
    )
    with connection.cursor() as cursor:
       cursor.execute("SELECT uomid, uomname FROM unitofmeasurement")
       unitofmeasurement_list = cursor.fetchall()  # Fetch all traders from DB
       unitofmeasurement_list = [{'id': row[0], 'name': row[1]} for row in unitofmeasurement_list]
 
    if request.method == 'POST':
        form = ItemDetailForm(request.POST)
        formset = BOMFormSet(request.POST)
 
        if form.is_valid():
            # Save parent ItemDetail first
            item = form.save(commit=False)
            item.save()  # Now commit the save for ItemDetail
 
            # Link the formset instance with the saved ItemDetail
            formset.instance = item
 
            # Check if the BOM formset is valid
            if formset.is_valid():
                formset.save()  # Save the BOM details
 
                # Saving child records (BOM details) manually if needed
                item_codes = request.POST.getlist('item_code[]')
                item_names = request.POST.getlist('item_name[]')
                required_qty = request.POST.getlist('required_qty[]')
 
                # Loop through each BOM entry and save it manually
                for i in range(len(item_codes)):
                    if item_codes[i]:
                        BillOfMaterials.objects.create(
                            item=item,  # Link to the parent item
                            item_code=item_codes[i],
                            item_name=item_names[i],
                            required_qty=required_qty[i],
                        )
 
                messages.success(request, "Item and BOM details added successfully!")
                return redirect('item_list')  # Redirect after saving
            else:
                # Debugging: print BOM formset errors
                print("BOM Formset Errors:", formset.errors)
                messages.error(request, "Failed to add BOM details. Please correct the errors.")
        else:
            # Debugging: print Item form errors
            print("Item Form Errors:", form.errors)
            messages.error(request, "Failed to add the Item. Please correct the errors.")
 
    else:
        form = ItemDetailForm()  # Empty form to display
        formset = BOMFormSet()  # Empty formset for BOM details
 
    return render(request, 'master/item_form.html', {
        'form': form,
        'bom_formset': formset,
        'title': 'Add New Item',
        'uoms': unitofmeasurement_list
    })
 
 
def item_edit(request, pk):
    """Edit an existing Item and its BOM details."""
    item = get_object_or_404(ItemDetail, pk=pk)
 
    BOMFormSet = inlineformset_factory(
        ItemDetail, BillOfMaterials, form=BillOfMaterialsForm, 
        extra=1, can_delete=True
    )
 
    if request.method == 'POST':
        form = ItemDetailForm(request.POST, instance=item)
        formset = BOMFormSet(request.POST, instance=item)
 
        if form.is_valid() and formset.is_valid():
            item = form.save(commit=False)  # Save the parent ItemDetail first
            item.save()  # Ensure it is saved before linking BOM
            formset.instance = item  # Assign the item to the BOM formset
            formset.save()  # Save the BOM records
 
            return redirect('item_list')  # Redirect to the list page
 
        else:
            print("Form Errors:", form.errors)
            print("Formset Errors:", formset.errors)
 
    else:
        form = ItemDetailForm(instance=item)
        formset = BOMFormSet(instance=item)
 
    return render(request, 'master/item_form.html', {
        'form': form,
        'bom_formset': formset,
        'title': 'Edit Item',
    })
 
 
def item_delete(request, pk):
    """Delete an Item along with its BOM entries."""
    item = get_object_or_404(ItemDetail, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('item_list')
 
    return render(request, 'master/item_form.html', {'item': item, 'item_master': ItemDetail.objects.all(), 'title': 'Delete Item'})
 
def item_detail(request, pk):
    """Display an Item in view-only mode, along with its BOM details."""
    item = get_object_or_404(ItemDetail, pk=pk)
 
    # Ensure BOMFormSet is correctly initialized
    BOMFormSet = inlineformset_factory(
        ItemDetail, BillOfMaterials, form=BillOfMaterialsForm, extra=0, can_delete=False
    )
 
    form = ItemDetailForm(instance=item)  # Parent Form
    bom_formset = BOMFormSet(instance=item)  # Child Formset linked to the parent ItemDetail
 
    return render(request, 'master/item_form.html', {
        'form': form,
        'bom_formset': bom_formset,
        'title': 'View Item',
        'view_mode': True  # Used to disable editing in the template
    })



# Store
 
def store_list(request):

    """Display all store with options to add, edit, and delete."""

    store = StoreDetail.objects.all()

    return render(request, 'master/store_list.html', {'store': store})
 
def store_add(request):

    """Add a new store."""

    if request.method == 'POST':

        form = StoreDetailForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect('store_list')

    else:

        form = StoreDetailForm()
 
    return render(request, 'master/store_detail_form.html', {'form': form, 'title': 'Add Store', "hide_logout": True})
 
def store_edit(request, pk):

    """Edit an existing store."""

    store = get_object_or_404(StoreDetail, pk=pk)

    if request.method == 'POST':

        form = StoreDetailForm(request.POST, instance=store)

        if form.is_valid():

            form.save()

            return redirect('store_list')

    else:

        form = StoreDetailForm(instance=store)
 
    return render(request, 'master/store_detail_form.html', {'form': form, 'title': 'Edit Store', "hide_logout": True})
 
def store_delete(request, pk):

    """Delete a store."""

    store = get_object_or_404(StoreDetail, pk=pk)

    if request.method == 'POST':

        store.delete()

        return redirect('store_list')

    return render(request, 'master/store_detail_form.html', {'store': store})
 
def store_view(request, pk):

   """Display a store in view-only mode."""

   store = get_object_or_404(StoreDetail, pk=pk)

   form = StoreDetailForm(instance=store)

   return render(request, 'master/store_detail_form.html', {'form': form, 'title': 'View Store', 'view_mode': True, "hide_logout": True})
 

#Bag_Boxes

#/*   Bag_Boxes        bag_boxes  *     /

def bag_boxes_list(request):
    """Display all bag_boxes with options to add, edit, and delete."""
    bag_boxes = Bag_BoxesDetails.objects.all()
    return render(request, 'master/bag_boxes_list.html', {'bag_boxes': bag_boxes})

def bag_boxes_add(request):
    """Add a new bag_boxes."""
    if request.method == 'POST':
        form = Bag_BoxesDetailForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('bag_boxes_list')
    else:
        form = Bag_BoxesDetailForm()

    return render(request, 'master/bag_boxes_detail_form.html', {'form': form, 'title': 'Add Bag_Boxes', "hide_logout": True})

def bag_boxes_edit(request, pk):
    """Edit an existing bag_boxes."""
    bag_boxes = get_object_or_404(Bag_BoxesDetails, pk=pk)
    if request.method == 'POST':
        form = Bag_BoxesDetailForm(request.POST, instance=bag_boxes)
        if form.is_valid():
            form.save()
            return redirect('bag_boxes_list')
    else:
        form = Bag_BoxesDetailForm(instance=bag_boxes)

    return render(request, 'master/bag_boxes_detail_form.html', {'form': form, 'title': 'Edit Bag_Boxes', "hide_logout": True})

def bag_boxes_delete(request, pk):
    """Delete a bag_boxes."""
    bag_boxes = get_object_or_404(Bag_BoxesDetails, pk=pk)
    if request.method == 'POST':
        bag_boxes.delete()
        return redirect('bag_boxes_list')
    
    return render(request, 'master/bag_boxes_detail_form.html', {'bag_boxes': bag_boxes})  #/*   Bag_Boxes        bag_boxes  *     /

def bag_boxes_view(request, pk):
   """Display a bag_boxes in view-only mode."""
   bag_boxes= get_object_or_404(Bag_BoxesDetails, pk=pk)
   form = Bag_BoxesDetailForm(instance=bag_boxes)
    
   return render(request, 'master/bag_boxes_detail_form.html', {'form': form, 'title': 'View Bag_Boxes', 'view_mode': True, "hide_logout": True})

def get_user_location(request):
    username = request.GET.get('username', '').strip()
    print(f"Received Username: {username}")  # Debugging log

    if username:
        user = User.objects.filter(name__iexact=username).first()
        if user:
            print(f"User Found: {user.name}, Location: {user.location}")
            return JsonResponse({'location': user.location})
    
    print("User Not Found")
    return JsonResponse({'location': None})