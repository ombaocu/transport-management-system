# -*- coding: utf-8 -*-
# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Mexican Localization TMS General Ledger',
    'version': '10.0.0.1.0',
    'category': 'Accounting',
    'author': 'Jarsa Sistemas',
    'website': 'https://www.jarsa.com.mx',
    'depends': ['tms'],
    'summary': (
        'This module creates a general ledger based on mexican legislations '
        'for freights'),
    'license': 'AGPL-3',
    'data': [
        'wizards/account_general_ledger_view.xml',
        'views/account_move_view.xml',
    ],
    'application': False,
    'installable': True,
}
