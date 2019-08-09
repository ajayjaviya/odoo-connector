# -*- coding: utf-8 -*-
{'name': 'Magento Connector',
 'version': '11.0.1',
 'category': 'Connector',
 'depends': ['sale_stock'],
 'author': "Ajay Javiya",
 'data': [
     'security/ir.model.access.csv',
     'data/product_cron.xml',
     'views/magento_view.xml',
     'views/magento_store_view.xml',
     'views/product_view.xml',
     'views/magento_attribute_view.xml',
 ],
 'installable': True,
 'application': False,
 }
