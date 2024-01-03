{
    'name': 'ZC Sales - Arnaldo Castro',
    'version': '16.0.0.1',
    'summary': 'ZC Sales - Arnaldo Castro',
    'author': 'Arnaldo Castro',
    'company': 'Arnaldo Castro',
    'maintainer': 'Arnaldo Castro',
    'sequence': 4,
    'license': 'LGPL-3',
    'description': """ZC Sales - Arnaldo Castro""",
    'category': 'Connector',
    'depends': [
        'base', 'sale', 'account', 'stock', 'sale_renting'
    ],
    'data': [
        'views/account_cash_rounding_view.xml',
        'views/product_template_view.xml',
        'views/sale_order_rental_view.xml',
        'views/sale_order_view.xml',
        'wizard/wizard_report_sale.xml',
        'security/ir.model.access.csv'
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
