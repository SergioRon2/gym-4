# Generated by Django 4.2.6 on 2023-11-28 05:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gymapp', '0029_articulo_registroganancia_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='registroganancia',
            name='gasto_diario',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='registroganancia',
            name='gasto_mensual',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.CreateModel(
            name='DetalleVenta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad_vendida', models.IntegerField(default=0)),
                ('articulo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gymapp.articulo')),
                ('registro_ganancia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gymapp.registroganancia')),
            ],
        ),
        migrations.AddField(
            model_name='registroganancia',
            name='articulos_vendidos',
            field=models.ManyToManyField(through='gymapp.DetalleVenta', to='gymapp.articulo'),
        ),
    ]
