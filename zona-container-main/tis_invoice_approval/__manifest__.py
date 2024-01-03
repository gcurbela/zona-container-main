# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2023. All rights reserved.

{
    'name': 'Invoice Approval',
    'version': '16.0.0.0.0',
    'category': 'invoice',
    'summary': 'Invoice approvals',
    'sequence': 1,
    'price': 25,
    'currency': 'EUR',
    'author': 'Technaureus Info Solutions Pvt. Ltd.',
    'website': 'http://www.technaureus.com/',
    'description': 'This application allows to configure approvals for validating an invoice',
    'license': 'LGPL-3',
    'images': [
        'images/main_screenshot.png'],
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_templates.xml',
        'views/invoice_approval_views.xml',
        'views/res_config_settings_views.xml',
        'views/account_move_views.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
