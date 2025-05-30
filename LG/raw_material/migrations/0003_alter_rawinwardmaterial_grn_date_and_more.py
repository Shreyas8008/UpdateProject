# Generated by Django 5.1.7 on 2025-03-21 04:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('raw_material', '0002_rmlabelgeneration_rmmaterialissue_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rawinwardmaterial',
            name='grn_date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='rawinwardmaterial',
            name='grn_no',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='rmmaterialissue',
            name='date_of_issue',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='rmmaterialissue',
            name='iss_no',
            field=models.PositiveIntegerField(blank=True, null=True, unique=True),
        ),
    ]
