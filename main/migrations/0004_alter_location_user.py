# Generated by Django 4.0.1 on 2022-01-15 21:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_remove_user_region_location_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
