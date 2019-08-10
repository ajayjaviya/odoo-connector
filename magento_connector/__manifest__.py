# -*- coding: utf-8 -*-
{
    'name': 'Magento Connector',
    'version': '11.0.1',
    'category': 'Connector',
    'depends': ['sale_stock'],
    'author': "Ajay Javiya",
    'summary': 'Magento Odoo Connector',
    'description': """
        Magento 2 Odoo Connector is build using Magento 2 Rest API it Include Below Features

        * Import Store from Magento
        * Import the categories of products
        * Import the Attribute Set of Products
        * Import the products, stock quantities and image / media (only main image)
        * Export the products, stock quantities and image / media
        * Update the products, stock quantities and image / media
     """,
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
