from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from master.models import ItemDetail
from .forms import RawInwardMaterialForm, RawInwardMaterialSubForm
from .models import RawInwardMaterial, RawInwardMaterialSub


# List of Inward Materials
def inward_material_list(request):
    inward_materials = RawInwardMaterial.objects.all()
    return render(request, 'raw_material/inward_material_list.html', {
        'inward_materials': inward_materials
    })


# Add New Inward Material
def inward_material_add(request):
    item_master = ItemDetail.objects.all()

    if request.method == 'POST':
        form = RawInwardMaterialForm(request.POST)

        if form.is_valid():
            # Save Parent (Inward Material)
            inward_material = form.save()

            # Save Child (Item Details)
            item_codes = request.POST.getlist('item_code[]')
            item_names = request.POST.getlist('item_name[]')

            uoms = request.POST.getlist('uom[]')
            quantities = request.POST.getlist('quantity[]')
            no_of_bags = request.POST.getlist('no_of_bags[]')
            mfg_dates = request.POST.getlist('mfg_date[]')
            exp_dates = request.POST.getlist('exp_date[]')
            lot_nos = request.POST.getlist('lot_no[]')
            repacking_batch_nos = request.POST.getlist('repacking_batch_no[]')


            for i in range(len(item_codes)):
                if item_codes[i]:
                    RawInwardMaterialSub.objects.create(
                        inward_material=inward_material,
                        item_code=item_codes[i],
                        item_name=item_names[i],
                        uom=uoms[i],
                        quantity=quantities[i],
                        no_of_bags=no_of_bags[i],
                        mfg_date=mfg_dates[i],
                        exp_date=exp_dates[i],
                        lot_no=lot_nos[i],
                        repacking_batch_no=repacking_batch_nos[i],

                    )

            messages.success(request, "Inward Material added successfully!")
            return redirect('inward_material_list')
        else:
            messages.error(request, "Failed to add Inward Material. Please correct the errors.")
    else:
        form = RawInwardMaterialForm()

    return render(request, 'raw_material/inward_material_form.html', {
        'form': form,
        'item_master': item_master,
        'title': 'Add Inward Material'
    })


# Edit Inward Material
def inward_material_edit(request, id):
    inward_material = get_object_or_404(RawInwardMaterial, pk=id)
    form = RawInwardMaterialForm(request.POST or None, instance=inward_material)
    child_items = RawInwardMaterialSub.objects.filter(inward_material=inward_material)
    item_master = ItemDetail.objects.all()

# Create a form instance with existing data for each child item
    subforms = []
    for child_item in child_items:
        subform = RawInwardMaterialSubForm(instance=child_item)
        subforms.append(subform)

    if request.method == "POST":
        if form.is_valid():
            form.save()

            # Clear Old Items
            child_items.delete()

            # Save Updated Items
            item_codes = request.POST.getlist('item_code[]')
            item_names = request.POST.getlist('item_name[]')
            uoms = request.POST.getlist('uom[]')
            quantities = request.POST.getlist('quantity[]')
            no_of_bags = request.POST.getlist('no_of_bags[]')
            mfg_dates = request.POST.getlist('mfg_date[]')
            exp_dates = request.POST.getlist('exp_date[]')
            lot_nos = request.POST.getlist('lot_no[]')
            repacking_batch_nos = request.POST.getlist('repacking_batch_no[]')

            for i in range(len(item_names)):
                RawInwardMaterialSub.objects.create(
                    inward_material=inward_material,
                    item_code=item_codes[i],
                    item_name=item_names[i],
                    uom=uoms[i],
                    quantity=quantities[i],
                    no_of_bags=no_of_bags[i],
                    mfg_date=mfg_dates[i],
                    exp_date=exp_dates[i],
                    lot_no=lot_nos[i],
                    repacking_batch_no=repacking_batch_nos[i],
                )

            messages.success(request, "Inward Material updated successfully!")
            return redirect('inward_material_list')
        else:
            messages.error(request, "Failed to update Inward Material.")
    
    return render(request, 'raw_material/inward_material_form.html', {
        'form': form,
        'title': 'Edit Inward Material',
        'child_items': child_items,
        'item_master': item_master,
        'subforms': subforms,


    })


# View Inward Material
def inward_material_view(request, id):
    material = get_object_or_404(RawInwardMaterial, id=id)
    form = RawInwardMaterialForm(instance=material)
    child_items = RawInwardMaterialSub.objects.filter(inward_material=material)
    item_master = ItemDetail.objects.all()

    return render(request, 'raw_material/inward_material_form.html', {
        'form': form,
        'title': 'View Inward Material',
        'child_items': child_items,
        'view_mode': True,
        'item_master': item_master,

    })


# Delete Inward Material
def inward_material_delete(request, id):
    material = get_object_or_404(RawInwardMaterial, id=id)
    material.delete()
    messages.success(request, "Inward Material deleted successfully!")
    return redirect('inward_material_list')

