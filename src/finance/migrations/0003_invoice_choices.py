from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('finance', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='type',
            field=models.CharField(
                choices=[('nfe', 'NF-e'), ('nfce', 'NFC-e')],
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='status',
            field=models.CharField(
                choices=[
                    ('pendente', 'Pendente'),
                    ('autorizada', 'Autorizada'),
                    ('rejeitada', 'Rejeitada'),
                    ('cancelada', 'Cancelada'),
                ],
                default='pendente',
                max_length=30,
            ),
        ),
    ]
