# Generated by Django 4.1.13 on 2023-12-09 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('automacao', '0003_robodecisionmodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='robodecisionmodel',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='tradingdecision',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='weight',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
