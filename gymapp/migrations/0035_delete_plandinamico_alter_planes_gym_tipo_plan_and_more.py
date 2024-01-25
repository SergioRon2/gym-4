# Generated by Django 4.2.6 on 2024-01-25 04:48

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('gymapp', '0034_alter_usuario_gym_fecha_fin'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PlanDinamico',
        ),
        migrations.AlterField(
            model_name='planes_gym',
            name='tipo_plan',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='usuario_gym',
            name='fecha_fin',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='usuario_gym',
            name='fecha_inicio_gym',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
