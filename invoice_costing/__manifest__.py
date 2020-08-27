# -*- coding: utf-8 -*-

{
    'name': 'Accounting',
    'version': '1.1',
    'category': 'Accounting',
    'summary': 'Manage financial and Invoice Costing',
    'description': """
Accounting Access Rights
========================
It manages the invoice costing for the Accounting 
""",
    'website': 'http://ps-sa.net',
    'author': 'Arunagiri',
    'depends': ['account','base'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/account_invoice_views.xml',
        'views/vendor_bill_view.xml',
        'views/invoice_costing_view.xml',
        'security/ir.model.access.csv'
    ],
    'demo': [ ],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
