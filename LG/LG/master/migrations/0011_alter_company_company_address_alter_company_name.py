# Generated by Django 4.2.19 on 2025-03-07 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0010_remove_rawinwardmaterialsub_inward_material_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='company_address',
            field=models.TextField(verbose_name='company Address'),
        ),
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.CharField(max_length=255, verbose_name='company Name'),
        ),
    ]
