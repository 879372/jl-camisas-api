from django.db import migrations


def seed_quote_config(apps, schema_editor):
    quote_config = apps.get_model('quotes', 'QuoteConfig')
    if not quote_config.objects.exists():
        quote_config.objects.create()


class Migration(migrations.Migration):
    dependencies = [
        ('quotes', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_quote_config, migrations.RunPython.noop),
    ]
