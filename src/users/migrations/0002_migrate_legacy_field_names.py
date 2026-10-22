from django.db import migrations


def migrate_legacy_field_names(apps, schema_editor):
    """Rename columns created by the former Portuguese User model."""
    connection = schema_editor.connection
    table_name = 'users_user'
    if table_name not in connection.introspection.table_names():
        return

    with connection.cursor() as cursor:
        columns = {
            column.name
            for column in connection.introspection.get_table_description(cursor, table_name)
        }

    quoted_table = schema_editor.quote_name(table_name)
    if 'nome' in columns and 'name' not in columns:
        schema_editor.execute(
            f'ALTER TABLE {quoted_table} RENAME COLUMN '
            f'{schema_editor.quote_name("nome")} TO {schema_editor.quote_name("name")}'
        )
    if 'perfil' in columns and 'profile' not in columns:
        schema_editor.execute(
            f'ALTER TABLE {quoted_table} RENAME COLUMN '
            f'{schema_editor.quote_name("perfil")} TO {schema_editor.quote_name("profile")}'
        )


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(migrate_legacy_field_names, migrations.RunPython.noop),
    ]
