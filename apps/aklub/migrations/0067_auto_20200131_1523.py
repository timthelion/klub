# Generated by Django 2.2.9 on 2020-01-31 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aklub', '0066_auto_20200128_1502'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='petitionsignature',
            name='event',
        ),
        migrations.RemoveField(
            model_name='petitionsignature',
            name='user',
        ),
        migrations.AlterField(
            model_name='event',
            name='result',
            field=models.ManyToManyField(blank=True, to='interactions.Results', verbose_name='Acceptable results of communication'),
        ),
        migrations.DeleteModel(
            name='Interaction',
        ),
        migrations.DeleteModel(
            name='PetitionSignature',
        ),
    ]
