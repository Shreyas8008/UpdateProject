from django.shortcuts import render
from django.db.models import Sum, Value, DecimalField, Q
from django.db.models.functions import Coalesce
from decimal import Decimal, InvalidOperation
from master.models import ItemDetail, BillOfMaterials
from raw_material.models import RawInwardMaterialSub, RmMaterialIssueSub
from finished_goods.models import FGInwardMaterialSub, PackingSlipItem
from packing_materials.models import PackingInwardMaterialSub, pmmaterialissuesub


def check_material_availability_for_fg_inward(item_code, fg_quantity):
    bom_items = BillOfMaterials.objects.filter(item_code=item_code)
    low_stock_issues = []
    max_possible_fg_units = None
    for bom in bom_items:
        try:
            required_qty_per_unit = Decimal(bom.required_qty or 0)
            fg_qty = Decimal(fg_quantity)
        except (TypeError, InvalidOperation):
            required_qty_per_unit = Decimal(0)
            fg_qty = Decimal(0)

        total_required_qty = required_qty_per_unit * fg_qty
        component = bom.item
        component_code = component.item_code
        category_name = component.category.name

        if category_name == 'Raw Material':
            inward = RawInwardMaterialSub.objects.filter(item_code=component_code).aggregate(
    total=Coalesce(Sum('quantity', output_field=DecimalField()), Value(0, output_field=DecimalField()))
)['total']
            issued = RmMaterialIssueSub.objects.filter(item_code=component_code).aggregate(
    total=Coalesce(Sum('quantity', output_field=DecimalField()), Value(0, output_field=DecimalField()))
)['total']
        elif category_name == 'Packing Material':
            inward = PackingInwardMaterialSub.objects.filter(item_code=component_code).aggregate(
    total=Coalesce(Sum('quantity', output_field=DecimalField()), Value(0, output_field=DecimalField()))
)['total']
            issued = pmmaterialissuesub.objects.filter(item_code=component_code).aggregate(
    total=Coalesce(Sum('quantity', output_field=DecimalField()), Value(0, output_field=DecimalField()))
)['total']
        else:
            continue

        balance_qty = inward - issued

        if balance_qty < total_required_qty:
            low_stock_issues.append(
                f"❌ Insufficient '{component.item_name}' ({category_name}). Required: {total_required_qty}, Available: {balance_qty}"
            )

        if balance_qty - total_required_qty < 10:
            possible_fg_qty = (balance_qty - 10) / required_qty_per_unit if required_qty_per_unit else 0
            suggested_qty = int(possible_fg_qty) if possible_fg_qty > 0 else 0

            low_stock_issues.append(
                f"❌ Cannot inward {fg_quantity} units. '{component.item_name}' ({category_name}) "
                f"would go below minimum threshold (10 units).\n"
                f"✅ Suggest inwarding up to {suggested_qty} units based on current stock."
            )

            if max_possible_fg_units is None or suggested_qty < max_possible_fg_units:
                max_possible_fg_units = suggested_qty

    return low_stock_issues, max_possible_fg_units


def stock_statement(request):
    category_filter = request.GET.get('category', 'all')

    categories = {
        'raw_material': 'Raw Material',
        'packing_material': 'Packing Material',
        'finished_goods': 'Finished Goods'
    }

    inward_items = ItemDetail.objects.filter(
        Q(item_code__in=RawInwardMaterialSub.objects.values('item_code')) |
        Q(item_code__in=FGInwardMaterialSub.objects.values('item_code')) |
        Q(item_code__in=PackingInwardMaterialSub.objects.values('item_code'))
    ).distinct()

    if category_filter in categories:
        inward_items = inward_items.filter(category__name=categories[category_filter])

    stock_data = []

    for item in inward_items:
        item_code = item.item_code
        item_name = item.item_name
        category = item.category.name if item.category else "Unknown"
        rol = item.rol or Decimal(0)
        uom = item.uom or 'units'

        inward_raw = RawInwardMaterialSub.objects.filter(item_code=item_code).aggregate(
    total=Coalesce(Sum('quantity', output_field=DecimalField()), Value(0, output_field=DecimalField()))
)['total']
        inward_fg = FGInwardMaterialSub.objects.filter(item_code=item_code).aggregate(
    total=Coalesce(Sum('quantity', output_field=DecimalField()), Value(0, output_field=DecimalField()))
)['total']
        inward_packing = PackingInwardMaterialSub.objects.filter(item_code=item_code).aggregate(
    total=Coalesce(Sum('quantity', output_field=DecimalField()), Value(0, output_field=DecimalField()))
)['total']

        total_inward_stock = inward_raw + inward_fg + inward_packing

        issued_rm = RmMaterialIssueSub.objects.filter(item_code=item_code).aggregate(
    total=Coalesce(Sum('quantity', output_field=DecimalField()), Value(0, output_field=DecimalField()))
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
    total=Coalesce(Sum('quantity', output_field=DecimalField()), Value(0, output_field=DecimalField()))
)['total']

            deduction = required_qty * fg_produced_qty

            if category == "Raw Material":
                bom_rm_deduction += deduction
            elif category == "Packing Material":
                bom_pm_deduction += deduction

        total_issued_stock = issued_rm + issued_fg + issued_pm + bom_rm_deduction + bom_pm_deduction

        opening_stock = total_inward_stock - total_issued_stock
        closing_stock = opening_stock + total_inward_stock - total_issued_stock

        try:
            closing_val = Decimal(closing_stock)
        except:
            closing_val = Decimal(0)

        if opening_stock < 0:
            alert_type = 'critical'
            status_message = "❌ Critical Low Stock"
            play_beep = True
            needs_reorder = True
        elif closing_val < rol:
            alert_type = 'warning'
            status_message = "⚠️ Reorder Needed"
            play_beep = False
            needs_reorder = True
        else:
            alert_type = 'normal'
            status_message = "✅ Sufficient Stock"
            play_beep = False
            needs_reorder = False

        stock_data.append({
            'item_code': item_code,
            'item_name': item_name,
            'category': category,
            'rol': f"{rol} {uom}",
            'opening_stock': f"{opening_stock:.2f} {uom}",
            'inward_stock': f"{total_inward_stock:.2f} {uom}",
            'issued_stock': f"{total_issued_stock:.2f} {uom}",
            'closing_stock': f"{closing_stock:.2f} {uom}",
            'needs_reorder': needs_reorder,
            'alert_type': alert_type,
            'play_beep': play_beep,
            'status_message': status_message,
        })

    return render(request, 'stock_statement/stock_statement.html', {
        'stock_data': stock_data,
        'category_filter': category_filter,
        'categories': categories
    })
