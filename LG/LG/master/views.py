
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from .forms import VendorDetailForm,categoryForm,CustomerDetailForm,companyForm,ItemDetailForm
from .models import VendorDetail,category,CustomerDetail,company,ItemDetail
from django.http import JsonResponse
import json


def login_view(request):
    """Handle user login."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Redirect to vendor list after login
    else:
        form = AuthenticationForm()

    return render(request, 'master/login.html', {'form': form})

def home_view(request):
    """Render the home page (base.html)."""
    return render(request, 'base.html')
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

    return render(request, 'master/vendor_form.html', {'form': form, 'title': 'Add Vendor'})

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

    return render(request, 'master/vendor_form.html', {'form': form, 'title': 'Edit Vendor'})

def vendor_delete(request, pk):
    """Delete a vendor."""
    vendor = get_object_or_404(VendorDetail, pk=pk)
    if request.method == 'POST':
        vendor.delete()
        return redirect('vendor_list')
    
    return render(request, 'master/vendor_form.html', {'vendor': vendor})

def vendor_detail(request, pk):
   """Display a vendor in view-only mode."""
   vendor = get_object_or_404(VendorDetail, pk=pk)
   form = VendorDetailForm(instance=vendor)
    
   return render(request, 'master/vendor_form.html', {'form': form, 'title': 'View Vendor', 'view_mode': True})







def category_list(request):
    """Display all categories with options to add, edit, and delete."""
    categories = category.objects.all()
    return render(request, 'master/category_list.html', {'categories': categories})

def category_add(request):
    """Add a new category."""
    if request.method == 'POST':
        form = categoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = categoryForm()

    return render(request, 'master/category_form.html', {'form': form, 'title': 'Add Category'})

def category_edit(request, pk):
    """Edit an existing category."""
    category_instance = get_object_or_404(category, pk=pk)
    if request.method == 'POST':
        form = categoryForm(request.POST, instance=category_instance)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = categoryForm(instance=category_instance)

    return render(request, 'master/category_form.html', {'form': form, 'title': 'Edit Category'})

def category_delete(request, pk):
    """Delete a category."""
    category_instance = get_object_or_404(category, pk=pk)
    if request.method == 'POST':
        category_instance.delete()
        return redirect('category_list')

    return render(request, 'master/category_confirm_delete.html', {'category': category_instance})

def category_detail(request, pk):
    """View category details."""
    category_instance = get_object_or_404(category, pk=pk)
    form = categoryForm(instance=category_instance)

    return render(request, 'master/category_form.html', {'form': form, 'title': 'View Category', 'view_mode': True})



def customer_list(request):

    """Display all customers with options to add, edit, and delete."""

    customers = CustomerDetail.objects.all()

    return render(request, 'master/customer_list.html', {'customers': customers})
 
def customer_add(request):

    """Add a new customer."""

    if request.method == 'POST':

        form = CustomerDetailForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect('customer_list') #sucess

    else:

        form = CustomerDetailForm()
 
    return render(request, 'master/customer_detail_form.html', {'form': form, 'title': 'Add Customer'})
 
 
def customer_view(request, pk):

   """Display a Customer in view-only mode."""

   customer = get_object_or_404(CustomerDetail, pk=pk)

   form = CustomerDetailForm(instance=customer)

   return render(request, 'customer_detail_form.html', {'form': form, 'title': 'View Customer', 'view_mode': True})
 
 
def customer_edit(request, pk):

    """Edit an existing customer."""

    customer = get_object_or_404(CustomerDetail, pk=pk)

    if request.method == 'POST':

        form = CustomerDetailForm(request.POST, instance=customer)

        if form.is_valid():

            form.save()

            return redirect('customer_list')

    else:

        form = CustomerDetailForm(instance=customer)
 
    return render(request, 'master/customer_detail_form.html', {'form': form, 'title': 'Edit Customer'})
 
 
def customer_delete(request, pk):

    """Delete a customer."""

    customer = get_object_or_404(CustomerDetail, pk=pk)

    if request.method == 'POST':

        customer.delete()

        return redirect('customer_list')

    return render(request, 'customer_detail_form.html', {'customer_name': customer})




def company_form(request):
    if request.method == 'POST':
        # Handle the form submission
        form = companyForm(request.POST)
        
        # Check if the form is valid
        if form.is_valid():
            # Save the form data to the database
            form.save()
            # Redirect to the company list or success page after saving
            return redirect('company_form')  # Ensure the URL pattern is correct
    else:
        # If it's a GET request, show an empty form
        form = companyForm()

    # Render the form on the page
    return render(request, 'master/company_form.html', {'form': form})


def item_list(request):
    """Display all items with options to add, edit, and delete."""
    items = ItemDetail.objects.all()
    return render(request, 'master/item_list.html', {'items': items})

def item_add(request):
    """Add a new item."""
    if request.method == 'POST':
        form = ItemDetailForm(request.POST)
       
        if form.is_valid():
            form.save()
           
            return redirect('item_list')
    else:
        form = ItemDetailForm()
       
    return render(request, 'master/item_form.html', {'form': form,'title': 'Add Item'})
def item_add(request):
    if request.method == 'POST':
        print("📌 Received POST Data:", request.POST)  # Debugging line
        form = ItemDetailForm(request.POST)
        
        if form.is_valid():
            print("✅ Form is valid, saving now...")
            form.save()
            return redirect('item_list')
        else:
            print("❌ Form Errors:", form.errors)  # Debugging line

    else:
        form = ItemDetailForm()

    return render(request, 'master/item_form.html', {'form': form})

def item_edit(request, pk):
    """Edit an existing Item."""
    item = get_object_or_404(ItemDetail, pk=pk)
   
   
    if request.method == 'POST':
        form = ItemDetailForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
           
            return redirect('item_list')
    else:
        form = ItemDetailForm(instance=item)


    return render(request, 'master/item_form.html', {'form': form, 'title': 'Edit Item'})

def item_delete(request, pk):
    """Delete a Item."""
    item = get_object_or_404(ItemDetail, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('item_list')
    
    return render(request, 'master/item_form.html', {'item': item})

def item_detail(request, pk):
   """Display a item in view-only mode."""
   item = get_object_or_404(ItemDetail, pk=pk)
   form = ItemDetailForm(instance=item)
    
   return render(request, 'master/item_form.html', {'form': form, 'title': 'View Item', 'view_mode': True})


