from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from master.models import ItemDetail, StoreDetail
from .forms import FGInwardMaterialForm, FGInwardMaterialSubForm
from .models import FGInwardMaterial, FGInwardMaterialSub
from django.forms import modelformset_factory
from django.forms import inlineformset_factory
from django.http import HttpResponse
import base64
from io import BytesIO
import qrcode
from django.template.loader import render_to_string
from weasyprint import HTML
from master.models import ItemDetail, VendorDetail,StoreDetail,Bag_BoxesDetails


# List of Inward Materials
def finished_inward_material_list(request):
    finished_inward_materials = FGInwardMaterial.objects.all()
    return render(request, 'finished_goods/finished_inward_material_list.html', {
        'finished_inward_materials': finished_inward_materials
    })


# Add New Inward Material
def finished_inward_material_add(request):
    item_master = ItemDetail.objects.all()
    stores=StoreDetail.objects.all()

    if request.method == 'POST':
        form = FGInwardMaterialForm(request.POST)

        if form.is_valid():
            # Save Parent (Inward Material)
            inward_material = form.save()

            # Save Child (Item Details)
            item_codes = request.POST.getlist('item_code[]')
            item_names = request.POST.getlist('item_name[]')

            uoms = request.POST.getlist('uom[]')
            quantities = request.POST.getlist('quantity[]')
            box_no = request.POST.getlist('box_no[]')
            mfg_dates = request.POST.getlist('mfg_date[]')
            batch_nos = request.POST.getlist('batch_no[]')


            for i in range(len(item_codes)):
                if item_codes[i]:
                    FGInwardMaterialSub.objects.create(
                        inward_material=inward_material,
                        item_code=item_codes[i],
                        item_name=item_names[i],
                        uom=uoms[i],
                        quantity=quantities[i],
                        box_no=box_no[i],
                        mfg_date=mfg_dates[i],
                        batch_no=batch_nos[i],

                    )

            messages.success(request, "Inward Material added successfully!")
            return redirect('finished_inward_material_list')
        else:
            messages.error(request, "Failed to add Inward Material. Please correct the errors.")
    else:
        form = FGInwardMaterialForm()

    return render(request, 'finished_goods/finished_inward_material_form.html', {
        'form': form,
        'item_master': item_master,
        'stores':stores,
        'title': 'Add Inward Material',
        "hide_logout": True,
    })


# Edit Inward Material
def finished_inward_material_edit(request, id):
    inward_material = get_object_or_404(FGInwardMaterial, pk=id)
    form = FGInwardMaterialForm(request.POST or None, instance=inward_material)
    child_items = FGInwardMaterialSub.objects.filter(inward_material=inward_material)
    item_master = ItemDetail.objects.all()  # Fetch all item details
    stores=StoreDetail.objects.all()


    # Create a form instance with existing data for each child item
    subforms = [FGInwardMaterialSubForm(instance=child_item) for child_item in child_items]

    if request.method == "POST":
        if form.is_valid():
            form.save()

            # Clear Old Items
            child_items.delete()

            # Retrieve Updated Items
            item_codes = request.POST.getlist('item_code[]')
            item_names = request.POST.getlist('item_name[]')
            uoms = request.POST.getlist('uom[]')
            quantities = request.POST.getlist('quantity[]')
            box_no = request.POST.getlist('box_no[]')
            mfg_dates = request.POST.getlist('mfg_date[]')
            batch_nos = request.POST.getlist('batch_no[]')

            for i in range(len(item_names)):
                FGInwardMaterialSub.objects.create(
                    inward_material=inward_material,
                        item_code=item_codes[i],
                        item_name=item_names[i],
                        uom=uoms[i],
                        quantity=quantities[i],
                        box_no=box_no[i],
                        mfg_date=mfg_dates[i],
                        batch_no=batch_nos[i],
                )

            messages.success(request, "Inward Material updated successfully!")
            return redirect('finished_inward_material_list')
        else:
            messages.error(request, "Failed to update Inward Material.")

    return render(request, 'finished_goods/finished_inward_material_form.html', {
        'form': form,
        'title': 'Edit Inward Material',
        'child_items': child_items,  # Pass child items
        'item_master': item_master,
        'stores':stores,
        'subforms': subforms,
        "hide_logout": True,


    })


# View Inward Material
def finished_inward_material_view(request, id):
    material = get_object_or_404(FGInwardMaterial, id=id)
    form = FGInwardMaterialForm(instance=material)
    child_items = FGInwardMaterialSub.objects.filter(inward_material=material)
    item_master = ItemDetail.objects.all()
    stores=StoreDetail.objects.all()



    return render(request, 'finished_goods/finished_inward_material_form.html', {
        'form': form,
        'title': 'View Inward Material',
        'child_items': child_items,
        'view_mode': True,
        'item_master': item_master,
        'stores':stores,
        "hide_logout": True,

    })


# Delete Inward Material
def finished_inward_material_delete(request, id):
    material = get_object_or_404(FGInwardMaterial, id=id)
    material.delete()
    messages.success(request, "Inward Material deleted successfully!")
    return redirect('finished_inward_material_list')


from django.shortcuts import render, redirect, get_object_or_404
from .models import PackingSlip, PackingSlipItem, FGLabelGeneration, CustomerDetail, ItemDetail
from .forms import PackingSlipForm, PackingSlipItemForm, FGLabelGenerationForm

import logging
logger = logging.getLogger('finished_goods.packing_slip')



def create_packing_slip(request):
    customers = CustomerDetail.objects.all()
    item_master = ItemDetail.objects.all()

    if request.method == 'POST':
        form = PackingSlipForm(request.POST)

        if form.is_valid():
            packing_slip = form.save()

            # Estimate number of rows based on one of the fields
            row_count = 0
            while True:
                if request.POST.get(f'item_code_{row_count + 1}'):
                    row_count += 1
                else:
                    break

            # Loop through each row and extract values
            for i in range(1, row_count + 1):
                item_code = request.POST.get(f'item_code_{i}')
                item_name = request.POST.get(f'item_name_{i}')
                uom = request.POST.get(f'uom_{i}')
                box_bags = request.POST.get(f'box_bags_{i}')
                batch_no = request.POST.get(f'batch_no_{i}')
                qty = request.POST.get(f'qty_{i}')
                bal_qty = request.POST.get(f'bal_qty_{i}')
                stock_qty = request.POST.get(f'stock_qty_{i}')

                if item_code and item_name:
                    PackingSlipItem.objects.create(
                        packing_slip=packing_slip,
                        item_code=item_code,
                        item_name=item_name,
                        uom=uom,
                        box_bags=box_bags or 0,
                        batch_no=batch_no,
                        qty=qty or 0,
                        bal_qty=bal_qty or 0,
                        stock_qty=stock_qty or 0,
                    )

            return redirect('packing_slip_list')

        return render(request, 'finished_goods/create_packing_slip.html', {
            'packing_slip_form': form,
            'customers': customers,
            'item_master': item_master,
            'formset': [],
            'view_mode': False,
        })

    else:
        form = PackingSlipForm()
        return render(request, 'finished_goods/create_packing_slip.html', {
            'packing_slip_form': form,
            'customers': customers,
            'item_master': item_master,
            'formset': [],
            'view_mode': False,
        })








def packing_slip_list(request):
    packing_slips = PackingSlip.objects.all()
    return render(request, 'finished_goods/packing_slip_list.html', {'packing_slips': packing_slips})

def edit_packing_slip(request, pk):
    packing_slip = get_object_or_404(PackingSlip, pk=pk)
    
    # Use inlineformset_factory to create the formset for PackingSlipItem
    PackingSlipItemFormSet = inlineformset_factory(PackingSlip, PackingSlipItem, form=PackingSlipItemForm, extra=0)

    if request.method == 'POST':
        form = PackingSlipForm(request.POST, instance=packing_slip)
        formset = PackingSlipItemFormSet(request.POST, instance=packing_slip)
        
        if form.is_valid() and formset.is_valid():
            form.save()  # Save parent (PackingSlip)
            formset.save()  # Save children (PackingSlipItem)
            return redirect('packing_slip_list')  # Redirect to packing slip list after save
    else:
        form = PackingSlipForm(instance=packing_slip)
        formset = PackingSlipItemFormSet(instance=packing_slip)
    
    context = {
        'form': form,
        'formset': formset,  # Pass the formset to the template
        'customers': CustomerDetail.objects.all(),
        'item_master': ItemDetail.objects.all(),
        'view_mode': False,  # Allow editing mode
    }
    
    return render(request, 'finished_goods/create_packing_slip.html', context)





# def edit_packing_slip(request, pk):
#     packing_slip = get_object_or_404(PackingSlip, pk=pk)
    
#     # Define the inline formset for PackingSlipItem
#     PackingSlipItemFormSet = inlineformset_factory(PackingSlip, PackingSlipItem, form=PackingSlipItemForm, extra=1)
    
#     if request.method == 'POST':
#         # Create a form and formset from the POST data, bound to the existing packing_slip
#         form = PackingSlipForm(request.POST, instance=packing_slip)
#         formset = PackingSlipItemFormSet(request.POST, instance=packing_slip)
        
#         # Validate both the parent form and child formset
#         if form.is_valid() and formset.is_valid():
#             # Save both the parent (PackingSlip) and child (PackingSlipItem) instances
#             form.save()  # Save parent PackingSlip
#             formset.save()  # Save child PackingSlipItem instances

#             # Redirect to the packing slip list page after successful save
#             return redirect('packing_slip_list')
#     else:
#         # If the request is GET, initialize the forms with the existing PackingSlip instance
#         form = PackingSlipForm(instance=packing_slip)
#         formset = PackingSlipItemFormSet(instance=packing_slip)
    
#     # Render the template with the form and formset
#     return render(request, 'finished_goods/create_packing_slip.html', {'form': form, 'formset': formset ,"hide_logout": True,})


# views.py
from django.forms import modelformset_factory

def view_packing_slip(request, pk):
    packing_slip = get_object_or_404(PackingSlip, pk=pk)
    child_items = PackingSlipItem.objects.filter(packing_slip=packing_slip)

    # Create a formset for PackingSlipItem
    PackingSlipItemFormSet = modelformset_factory(PackingSlipItem, form=PackingSlipItemForm, extra=0)

    # Populate the formset with child items
    formset = PackingSlipItemFormSet(queryset=child_items)

    # Query data for dropdowns
    customers = CustomerDetail.objects.all()
    item_master = ItemDetail.objects.all()

    # Main form for Packing Slip
    form = PackingSlipForm(instance=packing_slip)

    context = {
        'form': form,
        'formset': formset,  # Pass the formset to the template
        'customers': customers,
        'item_master': item_master,
        'view_mode': True,  # Read-only mode
    }
    return render(request, 'finished_goods/create_packing_slip.html', context)


def delete_packing_slip(request, pk):
    packing_slip = get_object_or_404(PackingSlip, pk=pk)
    if request.method == "POST":
        packing_slip.delete()
        return redirect('packing_slip_list')
    return render(request, 'finished_goods/delete_packing_slip.html', {'packing_slip': packing_slip})


def add_packing_slip(request):
    if request.method == "POST":
        packing_slip_form = PackingSlipForm(request.POST)
        if packing_slip_form.is_valid():
            try:
                packing_slip = packing_slip_form.save(commit=False)
                packing_slip.po_date = request.POST.get('po_date')  # Ensure PO date is in date format
                packing_slip.save()

                # Add Packing Slip Items
                item_codes = request.POST.getlist('item_code')
                item_names = request.POST.getlist('item_name')
                uoms = request.POST.getlist('uom')
                box_bags = request.POST.getlist('box_bags')
                batch_nos = request.POST.getlist('batch_no')
                qtys = request.POST.getlist('qty')
                bal_qtys = request.POST.getlist('bal_qty')
                stock_qtys = request.POST.getlist('stock_qty')

                for i in range(len(item_codes)):
                    PackingSlipItem.objects.create(
                        packing_slip=packing_slip,
                        item_code=ItemDetail.objects.get(id=item_codes[i]),
                        item_name=item_names[i],
                        uom=uoms[i],
                        box_bags=box_bags[i],
                        batch_no=batch_nos[i],
                        qty=qtys[i],
                        bal_qty=bal_qtys[i],
                        stock_qty=stock_qtys[i]
                    )
                
                logger.info("Packing slip and items saved successfully")
                return redirect('packing_slip_list')
            except Exception as e:
                logger.error(f"Error saving packing slip: {e}")
                return HttpResponse("There was an error saving the packing slip. Please try again later.", status=500)
        else:
            logger.error("Packing slip form is invalid")
            logger.error(packing_slip_form.errors)
            return HttpResponse("Invalid form data. Please check your input.", status=400)
    else:
        packing_slip_form = PackingSlipForm()

    customers = CustomerDetail.objects.all()
    items = ItemDetail.objects.all()

    return render(request, 'finished_goods/create_packing_slip.html', {
        'packing_slip_form': packing_slip_form,
        'customers': customers,
        'items': items,
        "hide_logout": True,
    })

logger = logging.getLogger('finished_goods.fg_label')


def create_fg_label(request):
    if request.method == "POST":
        fg_label_form = FGLabelGenerationForm(request.POST)

        if fg_label_form.is_valid():
            try:
                fg_label = fg_label_form.save(commit=False)

                # Get item_code from form
                item_code = fg_label_form.cleaned_data.get('item_code')

                if not item_code:
                    logger.error("Item code is missing from form data.")
                    return HttpResponse("Item code is required. Please select an item.", status=400)

                # If item_code is an ID, fetch the ItemDetail instance
                if isinstance(item_code, int) or isinstance(item_code, str):
                    item_detail = ItemDetail.objects.get(id=int(item_code))  # ? Fetch instance using ID
                else:
                    item_detail = item_code  # Already an instance

                # Assign the ItemDetail instance to FGLabelGeneration
                fg_label.item_code = item_detail  # ? Assign FK instance
                fg_label.item_name = item_detail.item_name  # Assign related data

                # Save the FG Label
                fg_label.save()
                logger.info("FG Label saved successfully")
                return redirect('fg_label_list')

            except ItemDetail.DoesNotExist:
                logger.error("Selected ItemDetail does not exist.")
                return HttpResponse("Selected item does not exist.", status=400)

            except Exception as e:
                logger.error(f"Error saving FG label: {e}", exc_info=True)
                return HttpResponse(f"Error saving FG label: {e}", status=500)

        else:
            logger.error("FG label form is invalid")
            logger.error(fg_label_form.errors)
            return render(request, 'finished_goods/create_fg_label.html', {
                'fg_label_form': fg_label_form,
                'items': ItemDetail.objects.all(),
                'form_errors': fg_label_form.errors,
            })

    else:
        fg_label_form = FGLabelGenerationForm()

    items = ItemDetail.objects.all()

    return render(request, 'finished_goods/create_fg_label.html', {
        'fg_label_form': fg_label_form,
        'items': items,
        "hide_logout": True,
    })


def fg_label_list(request):
    fg_labels = FGLabelGeneration.objects.all()
    return render(request, 'finished_goods/fg_label_list.html', {'fg_labels': fg_labels})

def edit_fg_label(request, pk):
    fg_label = get_object_or_404(FGLabelGeneration, pk=pk)
    if request.method == "POST":
        fg_label_form = FGLabelGenerationForm(request.POST, instance=fg_label)
        if fg_label_form.is_valid():
            fg_label = fg_label_form.save(commit=False)
            fg_label.item_name = fg_label.item_code.item_name  # Set item_name from item_code
            fg_label.save()
            return redirect('fg_label_list')
    else:
        fg_label_form = FGLabelGenerationForm(instance=fg_label)

    items = ItemDetail.objects.all()
    return render(request, 'finished_goods/edit_fg_label.html', {
        'fg_label_form': fg_label_form,
        'fg_label': fg_label,
        'items': items,
        "hide_logout": True,
    })

def delete_fg_label(request, pk):
    fg_label = get_object_or_404(FGLabelGeneration, pk=pk)
    if request.method == "POST":
        fg_label.delete()
        return redirect('fg_label_list')
    return render(request, 'finished_goods/delete_fg_label.html', {'fg_label': fg_label})



from django.shortcuts import render, get_object_or_404
from finished_goods.models import FGLabelGeneration  # Assuming FGLabel is your model for the label details

def fg_label_details(request, pk):
    # Fetch the label by ID, or return 404 if not found
    label = get_object_or_404(FGLabelGeneration, pk=pk)
    
    # Pass the label object to the template for rendering
    return render(request, 'finished_goods/fg_label_view.html', {'fg_label': label})




def generate_qr_code(data):
    qr = qrcode.make(data)
    buffered = BytesIO()
    qr.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def print_fg_label(request, pk):
    label = get_object_or_404(FGLabelGeneration, pk=pk)
    
    # Generate QR code data
    qr_data = (
        f"Item Code: {label.item_code.item_code}\n"
        f"Item Name: {label.item_code.item_name}\n"
        f"Batch No: {label.batch_no}\n"
        f"Packing Qty: {label.packing_qty}\n"
        f"No of Bags: {label.no_of_bags}\n"
        f"Date of Packing: {label.date_of_packing}\n"
        f"Date of Expiry: {label.date_of_expiry}"
    )
    
    # Generate three QR codes
    qr_code_base64_1 = generate_qr_code(qr_data)
    qr_code_base64_2 = generate_qr_code(qr_data)
    qr_code_base64_3 = generate_qr_code(qr_data)
    
    # Render the HTML template with the label data and QR codes
    html_string = render_to_string('finished_goods/print_fg_label.html', {
        'label': label,
        'qr_code_base64_1': qr_code_base64_1,
        'qr_code_base64_2': qr_code_base64_2,
        'qr_code_base64_3': qr_code_base64_3,
    })
    
    # Convert the HTML to PDF
    html = HTML(string=html_string)
    pdf = html.write_pdf()
    
    # Return the PDF as a response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="label_{pk}.pdf"'
    return response
from django.shortcuts import render, get_object_or_404
from finished_goods.models import FGLabelGeneration, ItemDetail
from finished_goods.forms import FGLabelGenerationForm  # Assuming you have this form
from datetime import date
def fg_label_view(request, pk):
    label = get_object_or_404(FGLabelGeneration, pk=pk)
    item_master = ItemDetail.objects.all()

    form = FGLabelGenerationForm(instance=label)  # Bind the form to the model instance
    
    # Pass view_mode as True to disable form fields in view mode
    return render(request, 'finished_goods/create_fg_label.html', {
        'form': form,
        'item_master': item_master,
        'view_mode': True,  # Set to True for view mode (readonly)
    })