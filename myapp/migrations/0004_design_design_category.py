# Generated by Django 4.1 on 2022-10-01 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_design'),
    ]

    operations = [
        migrations.AddField(
            model_name='design',
            name='design_category',
            field=models.CharField(choices=[('RESIDENTAL', 'RESIDENTAL'), ('RETAILDESIGN', 'RETAILDESIGN'), ('SPACEADAPTATION', 'SPACEADAPTATION')], default='', max_length=100),
            preserve_default=False,
        ),
    ]
