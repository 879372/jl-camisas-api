from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0002_initial'),
    ]

    operations = [
        migrations.AddField(model_name='order', name='carrier', field=models.CharField(blank=True, max_length=200, null=True)),
        migrations.AddField(model_name='order', name='tracking_code', field=models.CharField(blank=True, max_length=100, null=True)),
        migrations.AddField(model_name='order', name='shipped_at', field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name='order', name='delivered_at', field=models.DateTimeField(blank=True, null=True)),
    ]
