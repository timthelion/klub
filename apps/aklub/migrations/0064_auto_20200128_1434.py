# Generated by Django 2.2.9 on 2020-01-28 13:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('aklub', '0063_auto_20200114_1732'),
    ]

    operations = [
        migrations.AddField(
            model_name='masscommunication',
            name='administrative_unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='aklub.AdministrativeUnit', verbose_name='administrative unit'),
        ),
        migrations.AlterField(
            model_name='administrativeunit',
            name='from_email_address',
            field=models.EmailField(default='kp@auto-mat.cz', help_text='Every new address has to be set up by system administrator', max_length=254, verbose_name='E-mail from address'),
        ),
    ]
