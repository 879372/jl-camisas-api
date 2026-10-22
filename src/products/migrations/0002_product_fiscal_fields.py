from decimal import Decimal

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(model_name='product', name='ncm', field=models.CharField(blank=True, max_length=8, null=True)),
        migrations.AddField(model_name='product', name='cest', field=models.CharField(blank=True, max_length=7, null=True)),
        migrations.AddField(model_name='product', name='cfop', field=models.CharField(blank=True, max_length=4, null=True)),
        migrations.AddField(
            model_name='product', name='origin',
            field=models.CharField(
                choices=[
                    ('0', 'Nacional'),
                    ('1', 'Estrangeira - importação direta'),
                    ('2', 'Estrangeira - adquirida no mercado interno'),
                    ('3', 'Nacional com conteúdo importado superior a 40%'),
                    ('5', 'Nacional com conteúdo importado inferior ou igual a 40%'),
                    ('8', 'Nacional com conteúdo importado superior a 70%'),
                ],
                default='0', max_length=1,
            ),
        ),
        migrations.AddField(model_name='product', name='icms_code', field=models.CharField(blank=True, max_length=3, null=True)),
        migrations.AddField(model_name='product', name='csosn', field=models.CharField(blank=True, max_length=3, null=True)),
        migrations.AddField(model_name='product', name='icms_rate', field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=5)),
        migrations.AddField(model_name='product', name='ipi_rate', field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=5)),
        migrations.AddField(model_name='product', name='pis_rate', field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=5)),
        migrations.AddField(model_name='product', name='cofins_rate', field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=5)),
    ]
