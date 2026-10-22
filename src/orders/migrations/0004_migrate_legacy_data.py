from django.core.management.color import no_style
from django.db import migrations


def _read_rows(connection, table_name, columns):
    if table_name not in connection.introspection.table_names():
        return []

    quote = connection.ops.quote_name
    with connection.cursor() as cursor:
        cursor.execute(
            f'SELECT {", ".join(quote(column) for column in columns)} '
            f'FROM {quote(table_name)}'
        )
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _copy_rows(connection, model, table_name, field_map):
    rows = _read_rows(connection, table_name, tuple(field_map))
    objects = [
        model(**{target: row[source] for source, target in field_map.items()})
        for row in rows
    ]
    if objects:
        model.objects.bulk_create(objects, ignore_conflicts=True)


def migrate_legacy_data(apps, schema_editor):
    """Copy records from the former Portuguese app tables without deleting them."""
    connection = schema_editor.connection
    Customer = apps.get_model('customers', 'Customer')
    Product = apps.get_model('products', 'Product')
    ProductVariation = apps.get_model('products', 'ProductVariation')
    Order = apps.get_model('orders', 'Order')
    OrderItem = apps.get_model('orders', 'OrderItem')
    OrderFile = apps.get_model('orders', 'OrderFile')
    OrderHistory = apps.get_model('orders', 'OrderHistory')
    Transaction = apps.get_model('finance', 'Transaction')
    Invoice = apps.get_model('finance', 'Invoice')
    QuoteConfig = apps.get_model('quotes', 'QuoteConfig')
    QuoteOption = apps.get_model('quotes', 'QuoteOption')

    _copy_rows(connection, Customer, 'clientes_cliente', {
        'id': 'id', 'created_at': 'created_at', 'updated_at': 'updated_at',
        'nome': 'name', 'tipo': 'type', 'cpf_cnpj': 'document_number',
        'email': 'email', 'telefone': 'phone', 'cep': 'postal_code',
        'logradouro': 'street', 'numero': 'number', 'complemento': 'complement',
        'bairro': 'neighborhood', 'cidade': 'city', 'uf': 'state',
        'data_nascimento': 'birth_date', 'observacoes': 'observations',
    })
    _copy_rows(connection, Product, 'produtos_produto', {
        'id': 'id', 'created_at': 'created_at', 'updated_at': 'updated_at',
        'nome': 'name', 'descricao': 'description', 'preco_base': 'base_price',
        'unidade': 'unit', 'ativo': 'is_active',
    })
    _copy_rows(connection, ProductVariation, 'produtos_produtovariacao', {
        'id': 'id', 'produto_id': 'product_id', 'nome': 'name',
        'valor_adicional': 'additional_price', 'ativo': 'is_active',
    })
    _copy_rows(connection, Order, 'pedidos_pedido', {
        'id': 'id', 'created_at': 'created_at', 'updated_at': 'updated_at',
        'numero': 'number', 'cliente_id': 'customer_id', 'status': 'status',
        'status_pagamento': 'payment_status', 'valor_total': 'total_amount',
        'valor_pago': 'paid_amount', 'data_entrega_prevista': 'expected_delivery_date',
        'observacoes': 'observations', 'observacoes_internas': 'internal_observations',
    })
    _copy_rows(connection, OrderItem, 'pedidos_pedidoitem', {
        'id': 'id', 'pedido_id': 'order_id', 'produto_id': 'product_id',
        'descricao': 'description', 'quantidade': 'quantity',
        'valor_unitario': 'unit_price', 'valor_total': 'total_price',
        'especificacoes': 'specifications',
    })
    _copy_rows(connection, OrderFile, 'pedidos_pedidoarquivo', {
        'id': 'id', 'pedido_id': 'order_id', 'nome_original': 'original_name',
        'caminho': 'file_path', 'mime_type': 'mime_type',
        'tamanho_bytes': 'size_bytes', 'uploaded_at': 'uploaded_at',
    })
    _copy_rows(connection, OrderHistory, 'pedidos_pedidohistorico', {
        'id': 'id', 'pedido_id': 'order_id', 'usuario_id': 'user_id',
        'acao': 'action', 'detalhe': 'detail', 'created_at': 'created_at',
    })
    _copy_rows(connection, Transaction, 'financeiro_lancamento', {
        'id': 'id', 'pedido_id': 'order_id', 'tipo': 'type',
        'descricao': 'description', 'valor': 'amount',
        'forma_pagamento': 'payment_method', 'data_lancamento': 'transaction_date',
        'observacoes': 'observations', 'created_at': 'created_at',
    })
    _copy_rows(connection, Invoice, 'financeiro_notafiscal', {
        'id': 'id', 'pedido_id': 'order_id', 'tipo': 'type', 'numero': 'number',
        'serie': 'series', 'chave_acesso': 'access_key', 'status': 'status',
        'xml': 'xml', 'protocolo': 'protocol', 'motivo_rejeicao': 'rejection_reason',
        'emitida_em': 'issued_at', 'created_at': 'created_at',
    })

    config_rows = _read_rows(connection, 'orcamento_orcamentoconfig', (
        'id', 'whatsapp_destino', 'mensagem_template', 'valor_base', 'ativo',
    ))
    for row in config_rows:
        QuoteConfig.objects.update_or_create(
            pk=row['id'],
            defaults={
                'whatsapp_destination': row['whatsapp_destino'],
                'message_template': row['mensagem_template'],
                'base_amount': row['valor_base'],
                'is_active': row['ativo'],
            },
        )
    _copy_rows(connection, QuoteOption, 'orcamento_orcamentoopcao', {
        'id': 'id', 'categoria': 'category', 'label': 'label',
        'valor_adicional': 'additional_amount', 'descricao': 'description',
        'icone': 'icon', 'ordem': 'order_index', 'ativo': 'is_active',
    })

    models = [
        Customer, Product, ProductVariation, Order, OrderItem, OrderFile,
        OrderHistory, Transaction, Invoice, QuoteConfig, QuoteOption,
    ]
    reset_sql = connection.ops.sequence_reset_sql(no_style(), models)
    with connection.cursor() as cursor:
        for statement in reset_sql:
            cursor.execute(statement)


class Migration(migrations.Migration):
    dependencies = [
        ('customers', '0001_initial'),
        ('products', '0002_product_fiscal_fields'),
        ('orders', '0003_order_distribution'),
        ('finance', '0003_invoice_choices'),
        ('quotes', '0002_seed_quote_config'),
        ('users', '0002_migrate_legacy_field_names'),
    ]

    operations = [
        migrations.RunPython(migrate_legacy_data, migrations.RunPython.noop),
    ]
