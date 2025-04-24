from django.shortcuts import render, get_object_or_404, redirect
from django.template import context
from .models import PMLabelGenerationItem
from .forms import PMLabelGenerationForm
import qrcode
import base64
from io import BytesIO
from django.http import JsonResponse
from django.contrib import messages
from master.models import ItemDetail, VendorDetail,StoreDetail,Bag_BoxesDetails
from .forms import PackingInwardMaterialForm, PackingInwardMaterialSubForm,pmmaterialissueForm, pmmaterialissuesubForm
from .models import PackingInwardMaterial, PackingInwardMaterialSub,pmmaterialissue, pmmaterialissuesub
from datetime import date
from .models import PurchaseOrder, PurchaseOrderItem, VendorDetail, ItemDetail
from .forms import PurchaseOrderForm, PurchaseOrderItemForm, PMLabelGenerationForm
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.forms import inlineformset_factory
from .models import UploadedFile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import  FileUploadForm


from datetime import date
from django.shortcuts import render, redirect
from .models import PMLabelGenerationItem, ItemDetail
from .forms import PMLabelGenerationForm

from datetime import datetime

def create_pm_label(request):
    item_master = ItemDetail.objects.all()

    if request.method == "POST":
        # Get data from POST
        noofpacks_list = request.POST.getlist("noofpacks")
        next_pack_no_list = request.POST.getlist("next_pack_no")
        lot_batch_no_list = request.POST.getlist("lot_batch_no")
        packing_qty_list = request.POST.getlist("packing_qty")
        item_code_list = request.POST.getlist("item_code")
        item_name_list = request.POST.getlist("item_name")
        receipt_date = request.POST.get("receipt_date")  # Get the date as string

        # Convert receipt_date string to a date object
        try:
            receipt_date = datetime.strptime(receipt_date, '%Y-%m-%d').date()
        except ValueError:
            # Handle the case where the date format is incorrect
            messages.error(request, "Invalid receipt date format. Please try again.")
            return redirect("create_pm_label")

        # Iterate and save data
        for i in range(len(item_code_list)):
            if item_code_list[i] and item_name_list[i]:
                PMLabelGenerationItem.objects.create(
                    item_code=item_code_list[i],
                    item_name=item_name_list[i],
                    noofpacks=noofpacks_list[i],
                    next_pack_no=next_pack_no_list[i],
                    lot_batch_no=lot_batch_no_list[i],
                    packing_qty=packing_qty_list[i],
                    receipt_date=receipt_date,  # Save the converted date
                )
        messages.success(request, "PM Label created successfully!")
        return redirect("pm_label_list")

    # If GET request
    else:
        form = PMLabelGenerationForm()

    return render(
        request, "packing_materials/create_pm_label.html",
        {
            "form": form,
            "item_master": item_master,
            "today": date.today(),
            "hide_logout": True,
        },
    )

def pm_label_list(request):
    labels = PMLabelGenerationItem.objects.all()
    return render(request, 'packing_materials/pm_label_list.html', {'labels': labels})
from django.views import View


from datetime import date

def pm_label_view(request, pk):
    label = get_object_or_404(PMLabelGenerationItem, pk=pk)
    item_master = ItemDetail.objects.all()

    form = PMLabelGenerationForm(instance=label, item_master=item_master)

    context = {
        'form': form,
        'item_master': item_master,
        'view_mode': True,  # Set to True for view mode (readonly)
        'today': date.today(),
    }

    return render(request, 'packing_materials/create_pm_label.html', context)


def edit_pm_label(request, pk):
    # Retrieve the label instance
    label = get_object_or_404(PMLabelGenerationItem, pk=pk)
    item_master = ItemDetail.objects.all()

    if request.method == "POST":
        # Bind the form with POST data and the instance
        form = PMLabelGenerationForm(request.POST, instance=label, item_master=item_master)
        if form.is_valid():
            # Save the updated instance
            form.save()
            messages.success(request, "PM Label updated successfully!")
            return redirect('pm_label_list')
        else:
            # Debugging: Print form errors to console
            print(form.errors)
            messages.error(request, "Please correct the errors below.")
    else:
        # Populate the form with instance data for GET request
        form = PMLabelGenerationForm(instance=label, item_master=item_master)

    # Render the template with context
    return render(request, 'packing_materials/create_pm_label.html', {
        'form': form,
        'label': label,
        'item_master': item_master,
        'view_mode': False,  # Ensure view_mode is False for editing
    })

def delete_pm_label(request, pk):
    label = get_object_or_404(PMLabelGenerationItem, pk=pk)
    label.delete()
    messages.success(request, "PM Label Generation deleted successfully!")
    return redirect('pm_label_list')

def print_pm_label(request, pk):
    label = get_object_or_404(PMLabelGenerationItem, pk=pk)

    # Generate QR Code
    qr_data = f"Item: {label.item_name}\nBatch: {label.lot_batch_no}\nReceipt Date: {label.receipt_date}"
    qr = qrcode.make(qr_data)
    qr_buffer = BytesIO()
    qr.save(qr_buffer, format="PNG")
    qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode()

    return render(request, 'packing_materials/print_pm_label.html', {'label': label, 'qr_code_base64': qr_base64})



# List of Inward Materials
# List of Inward Materials
def packing_material_list(request):
    packing_materials = PackingInwardMaterial.objects.all()
    return render(request, 'packing_materials/packing_material_list.html', {
        'packing_materials': packing_materials
    })


# Add New Inward Material
def packing_material_add(request):
    item_master = ItemDetail.objects.all()
    vendors=VendorDetail.objects.all()
    stores=StoreDetail.objects.all()
    bag_types=Bag_BoxesDetails.objects.all()
    today_date = date.today().strftime('%Y-%m-%d')

    if request.method == 'POST':
        form =PackingInwardMaterialForm(request.POST)

        if form.is_valid():
            packing_material = form.save(commit=False)
            if not packing_material.grn_no:
                packing_material.grn_no = PackingInwardMaterial.generate_next_grn_no()

            packing_material = form.save()
            

            # Save Child (Item Details)
            item_codes = request.POST.getlist('item_code[]')
            item_names = request.POST.getlist('item_name[]')

            uoms = request.POST.getlist('uom[]')
            quantities = request.POST.getlist('quantity[]')
            no_of_bags = request.POST.getlist('no_of_bags[]')
            recieved_dates = request.POST.getlist('recieved_date[]')
            

            for i in range(len(item_codes)):
                if item_codes[i]:
                    PackingInwardMaterialSub.objects.create(
                        packing_material=packing_material,
                        item_code=item_codes[i],
                        item_name=item_names[i],
                        uom=uoms[i],
                        quantity=quantities[i],
                        no_of_bags=no_of_bags[i],
                        recieved_date=recieved_dates[i],
                        

                    )

            messages.success(request, "packing Material added successfully!")
            return redirect('packing_material_list')
        else:
            messages.error(request, "Failed to add packing Material. Please correct the errors.")
    else:
        # ✅ Initial form with today's date pre-filled
        form = PackingInwardMaterialForm(initial={
            "grn_no": PackingInwardMaterial.generate_next_grn_no(),
            "grn_date": today_date,  # Default today's date for grn_date
        })

    return render(request, 'packing_materials/packing_material_form.html', {
        'form': form,
        'item_master': item_master,
        'vendors':vendors,
        'stores':stores,
        'bag_types':bag_types,
        'title': 'Add packing Material',
        'today_date': today_date,  # ✅ Pass today's date for use in template

    })


# Edit Inward Material
def packing_material_edit(request, id):
    packing_material = get_object_or_404(PackingInwardMaterial, pk=id)
    form = PackingInwardMaterialForm(request.POST or None, instance=packing_material)
    child_items = PackingInwardMaterialSub.objects.filter(packing_material=packing_material)
    item_master = ItemDetail.objects.all()  # Fetch all item details
    vendors=VendorDetail.objects.all()
    stores=StoreDetail.objects.all()
    bag_types=Bag_BoxesDetails.objects.all()

    today_date = packing_material.grn_date.strftime('%Y-%m-%d') if packing_material.grn_date else date.today().strftime('%Y-%m-%d')
    if request.method == 'POST':
        form = PackingInwardMaterialForm(request.POST, instance=packing_material)
    else:
        form = PackingInwardMaterialForm(instance=packing_material, initial={'grn_date': today_date})

    # Create a form instance with existing data for each child item
    subforms = [PackingInwardMaterialSubForm(instance=child_item) for child_item in child_items]

    if request.method == "POST":
        if form.is_valid():
            packing_material.grn_date = form.cleaned_data.get("grn_date", date.today())  # Ensure date is saved

            form.save()

            # Clear Old Items
            child_items.delete()

            # Retrieve Updated Items
            item_codes = request.POST.getlist('item_code[]')
            item_names = request.POST.getlist('item_name[]')
            uoms = request.POST.getlist('uom[]')
            quantities = request.POST.getlist('quantity[]')
            no_of_bags = request.POST.getlist('no_of_bags[]')
            recieved_dates = request.POST.getlist('recieved_date[]')

            for i in range(len(item_names)):
                PackingInwardMaterialSub.objects.create(
                    packing_material=packing_material,
                    item_code=item_codes[i],
                    item_name=item_names[i],
                    uom=uoms[i],
                    quantity=quantities[i],
                    no_of_bags=no_of_bags[i],
                   recieved_date=recieved_dates[i],
                        
                )

            messages.success(request, "Inward Material updated successfully!")
            return redirect('packing_material_list')
        else:
            messages.error(request, "Failed to update Inward Material.")

    return render(request, 'packing_materials/packing_material_form.html', {
        'form': form,
        'title': 'Edit packing Material',
        'child_items': child_items,  # Pass child items
        'item_master': item_master,
        'stores':stores,
        'subforms': subforms,
        'vendors':vendors,
        'bag_types':bag_types,
        'today_date': today_date,


    })


# View Inward Material
def packing_material_view(request, id):
    material = get_object_or_404(PackingInwardMaterial, id=id)
    form = PackingInwardMaterialForm(instance=material)
    child_items = PackingInwardMaterialSub.objects.filter(packing_material=material)
    item_master = ItemDetail.objects.all()
    vendors=VendorDetail.objects.all()
    stores=StoreDetail.objects.all()
    bag_types=Bag_BoxesDetails.objects.all()

    today_date = material.grn_date.strftime('%Y-%m-%d') if material.grn_date else date.today().strftime('%Y-%m-%d')
    form = PackingInwardMaterialForm(instance=material, initial={"grn_date": today_date})


    return render(request, 'packing_materials/packing_material_form.html', {
        'form': form,
        'title': 'View packing Material',
        'child_items': child_items,
        'view_mode': True,
        'item_master': item_master,
        'stores':stores,
        'vendors':vendors,
        'bag_types':bag_types,
         'today_date': today_date,
        'now': datetime.now(),

    })


# Delete Inward Material
def packing_material_delete(request, id):
    material = get_object_or_404(PackingInwardMaterial, id=id)
    material.delete()
    messages.success(request, "Inward Material deleted successfully!")
    return redirect('packing_material_list')

def get_items(request):
    items = list(ItemDetail.objects.values('item_code', 'item_name', 'uom'))
    return JsonResponse({'items': items})





# List of PM Material Issues
# List of PM Material Issues
def pm_material_issue_list(request):
    matIssueIds = pmmaterialissue.objects.all()
    return render(request, 'packing_materials/pm_material_issue_list.html', {
        'matIssueIds': matIssueIds
    })

#Add
def pm_material_issue_add(request):
    today_date = date.today().strftime("%Y-%m-%d")
    item_master = ItemDetail.objects.all()
    bag_types = Bag_BoxesDetails.objects.all()

    last_issue = pmmaterialissue.objects.order_by('-matIssueId').first()
    next_issue_no = (last_issue.matIssueId + 1) if last_issue else 1  

    if request.method == 'POST':
        form = pmmaterialissueForm(request.POST)

        # Manually assign fields not included in the form
        issue_to_whom = request.POST.get('issue_to_whom')
        bag_type_value = request.POST.get('bag_types')

        if form.is_valid():
            matIssue = form.save(commit=False)

            # Ensure manually assigned values are included
            matIssue.issue_to_whom = issue_to_whom
            matIssue.bag_types = bag_type_value

            # Assign defaults
            if not matIssue.issue_no:
                matIssue.issue_no = next_issue_no
            if not matIssue.issue_date:
                matIssue.issue_date = today_date

            matIssue.save()

            # Process child items
            item_codes = request.POST.getlist('item_code[]')
            item_names = request.POST.getlist('item_name[]')
            uoms = request.POST.getlist('uom[]')
            quantities = request.POST.getlist('quantity[]')
            stock_qtys = request.POST.getlist('stock_qty[]')
            total_bags = request.POST.getlist('total_bags[]')
            batch_nos = request.POST.getlist('batch_no[]')
            bags_issued = request.POST.getlist('bags_issued[]')

            for i in range(len(item_codes)):
                if item_codes[i] and item_names[i]:
                    pmmaterialissuesub.objects.create(
                        matIssueId=matIssue,
                        item_code=item_codes[i],
                        item_name=item_names[i],
                        uom=uoms[i],
                        quantity=quantities[i],
                        stock_qty=stock_qtys[i],
                        total_bags=total_bags[i],
                        batch_no=batch_nos[i],
                        bags_issued=bags_issued[i],
                    )

            messages.success(request, "PM Material Issue added successfully!")
            return redirect('pm_material_issue_list')
        else:
            print("Form errors:", form.errors)
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = pmmaterialissueForm(initial={
            "issue_no": next_issue_no,
            "issue_date": today_date,
        })

    return render(request, 'packing_materials/pm_material_issue_form.html', {
        'form': form,
        'item_master': item_master,
        'bag_types': bag_types,
        'title': 'Add PM Material Issue',
        'today_date': today_date,
        "hide_logout": True,
    })



# Edit PM Material Issue
def pm_material_issue_edit(request, matIssueId):
    issue = get_object_or_404(pmmaterialissue, pk=matIssueId)

    # 🔹 Ensure correct field name for the date
    today_date = issue.issue_date.strftime('%Y-%m-%d') if issue.issue_date else date.today().strftime('%Y-%m-%d')

    form = pmmaterialissueForm(request.POST or None, instance=issue, initial={"issue_date": today_date})
    child_items = pmmaterialissuesub.objects.filter(matIssueId=issue)
    item_master = ItemDetail.objects.all()
    bag_types = Bag_BoxesDetails.objects.all()

    if request.method == "POST":
        if form.is_valid():
            issue = form.save(commit=False)
            issue.issue_date = form.cleaned_data.get("issue_date", date.today())  # 🔹 Ensure issue_date is saved
            issue.save()

            # Clear Old Items
            child_items.delete()

            # Retrieve Updated Items
            item_codes = request.POST.getlist('item_code[]')
            item_names = request.POST.getlist('item_name[]')
            uoms = request.POST.getlist('uom[]')
            quantities = request.POST.getlist('quantity[]')
            stock_qtys = request.POST.getlist('stock_qty[]')
            total_bags = request.POST.getlist('total_bags[]')
            batch_nos = request.POST.getlist('batch_no[]')
            bags_issued = request.POST.getlist('bags_issued[]')

            for i in range(len(item_codes)):
                if item_codes[i]:  # Avoid creating empty records
                    pmmaterialissuesub.objects.create(
                        matIssueId=issue,
                        item_code=item_codes[i],
                        item_name=item_names[i],
                        uom=uoms[i],
                        quantity=quantities[i],
                        stock_qty=stock_qtys[i],
                        total_bags=total_bags[i],
                        batch_no=batch_nos[i],
                        bags_issued=bags_issued[i],
                    )

            messages.success(request, "PM Material Issue updated successfully!")
            return redirect('pm_material_issue_list')
        else:
            messages.error(request, "Failed to update PM Material Issue. Please check for errors.")

    return render(request, 'packing_materials/pm_material_issue_form.html', {
        'form': form,
        'title': 'Edit PM Material Issue',
        'child_items': child_items,
        'item_master': item_master,
        'bag_types': bag_types,
        'today_date': today_date,  # 🔹 Pass today_date for default value
        'issue_date': issue.issue_date.strftime('%Y-%m-%d') if issue.issue_date else '',  # 🔹 Ensure issue_date is passed
        "hide_logout": True,
    })
# View PM Material Issue
def pm_material_issue_view(request, matIssueId):
    issue = get_object_or_404(pmmaterialissue, pk=matIssueId)

    # 🔹 Ensure correct field name for the date
    today_date = issue.issue_date.strftime('%Y-%m-%d') if issue.issue_date else date.today().strftime('%Y-%m-%d')

    form = pmmaterialissueForm(instance=issue, initial={"issue_date": today_date})
    child_items = pmmaterialissuesub.objects.filter(matIssueId=issue)
    item_master = ItemDetail.objects.all()
    bag_types = Bag_BoxesDetails.objects.all()

    return render(request, 'packing_materials/pm_material_issue_form.html', {
        'form': form,
        'title': 'View PM Material Issue',
        'child_items': child_items,
        'view_mode': True,  # 🔹 Indicates read-only mode
        'item_master': item_master,
        'bag_types': bag_types,
        'today_date': today_date,  # 🔹 Pass today_date for consistency
        'issue_date': issue.issue_date.strftime('%Y-%m-%d') if issue.issue_date else '',  # 🔹 Ensure issue_date is passed
        "hide_logout": True,
    })

# Delete PM Material Issue
def pm_material_issue_delete(request, matIssueId):
    matIssueId = get_object_or_404(pmmaterialissue, matIssueId=matIssueId)
    matIssueId.delete()
    messages.success(request, "PM Material Issue deleted successfully!")
    return redirect('pm_material_issue_list')



def purchase_order_list(request):
    orders = PurchaseOrder.objects.all()
    return render(request, 'packing_materials/purchase_order_list.html', {'orders': orders})

def purchase_order_detail(request, pk):  # `pk` is coming from the URL
    order = get_object_or_404(PurchaseOrder, sl_no=pk)  # ✅ Use `sl_no` instead of `id`

    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save(commit=False)
            uploaded_file.purchase_order = order
            uploaded_file.uploaded_by = request.user
            uploaded_file.save()
            return redirect('purchase_order_detail', pk=order.sl_no)  # ✅ Use `sl_no`

    else:
        form = FileUploadForm()

    return render(request, "packing_materials/purchase_order_detail.html", {
        "order": order,
        "form": form

    })


def purchase_order_view(request, pk):
    """Display a Purchase Order in view-only mode."""
    order = get_object_or_404(PurchaseOrder, sl_no=pk)  # ✅ Use sl_no instead of id
    form = PurchaseOrderForm(instance=order)
    
    # Pass `view_mode` to disable fields in the template
    return render(request, 'packing_materials/purchase_order_form.html', {
        'form': form,
        'view_mode': True,
        "hide_logout": True,
    })


def purchase_order_create(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, request.FILES)
        if form.is_valid():
            order = form.save()
            return redirect('purchase_order_detail', pk=order.pk)
    else:
        form = PurchaseOrderForm()
    return render(request, 'packing_materials/purchase_order_form.html', {'form': form , "hide_logout": True,})

def purchase_order_edit(request, pk):
    order = get_object_or_404(PurchaseOrder, sl_no=pk)  # ✅ Use `sl_no` instead of `id`
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, request.FILES, instance=order)
        if form.is_valid():
            order = form.save()
            return redirect('purchase_order_detail', pk=order.sl_no)  # ✅ Redirect using `sl_no`
    else:
        form = PurchaseOrderForm(instance=order)
    return render(request, 'packing_materials/purchase_order_form.html', {'form': form,"hide_logout": True,})


def purchase_order_delete(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('purchase_order_list')
    return render(request, 'packing_materials/purchase_order_confirm_delete.html', {'order': order})



def pm_label_generation_item_list(request, pm_label_generation_id):
    pm_label_generation = get_object_or_404(PMLabelGenerationItem, id=pm_label_generation_id)
    pm_label_generation_items = PMLabelGenerationItem.objects.filter(pm_label_generation=pm_label_generation)
    
    return render(request, 'packing_materials/pm_label_generation_item_list.html', {
        'pm_label_generation': pm_label_generation,
        'pm_label_generation_items': pm_label_generation_items,
    })



from .models import UploadedFile

def edit_file(request, pk):
    file = UploadedFile.objects.get(pk=pk)
    if request.method == "POST":
        file.file_name = request.POST.get('file_name', file.file_name)
        file.save()
        return redirect('purchase_order_detail', pk=file.purchase_order.pk)
    return render(request, 'packing_materials/edit_file.html', {'file': file})

def delete_file(request, pk):
    file = UploadedFile.objects.get(pk=pk)
    order_pk = file.purchase_order.pk
    file.delete()
    return redirect('purchase_order_detail', pk=order_pk)



def save_uploaded_files(request):
    if request.method == "POST":
        files = request.FILES.getlist("files[]")  # Get all uploaded files
        file_types = request.POST.getlist("file_types[]")  # Get corresponding file types

        if not files:
            return JsonResponse({"success": False, "error": "No files received."}, status=400)

        saved_files = []
        for file, file_type in zip(files, file_types):
            file_name = f"uploads/{file.name}"
            file_path = default_storage.save(file_name, ContentFile(file.read()))  # Save file

            saved_files.append({
                "file_type": file_type,
                "file_name": os.path.basename(file_path),
                "file_url": default_storage.url(file_path),
            })

        return JsonResponse({"success": True, "files": saved_files})
    
    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)


