# Generated by Django 4.2.6 on 2024-03-12 04:57

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('gymapp', '0036_asistencia_hora'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='registroganancia',
            name='articulos_vendidos',
        ),
        migrations.AddField(
            model_name='registroganancia',
            name='total_mensual',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='asistencia',
            name='hora',
            field=models.TimeField(default=django.utils.timezone.now),
        ),
    ]
