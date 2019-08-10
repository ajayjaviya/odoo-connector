
Magento Odoo Connector
======================

Magento 2 Odoo Connector is build using Magento 2 Rest API it Include Below Features

* Import Store from Magento
* Import the categories of products
* Import the Attribute Set of Products
* Import the products, stock quantities and image / media (only main image)
* Export the products, stock quantities and image / media
* Update the products, stock quantities and image / media


Technical:
==========

* Built using Magento 2 Rest API
* Support Magento 2.x+
* Tested with odoo 11 and Magento 2.3

Configuration:
==============
*Create Access Token in Magento
    -> Login to Magento Admin
    -> Go to System > Extensions > Integrations > Add new Integrations > Fill Detail
    -> Copy Access Token generate by Magento

*Create Connection in Odoo
    -> Go Magento > Magento > Magento Instance > Create new Instance
        - eg. Location http://m2.com
        - Access Token : Add access token generated form Magento

Aussumption:
============

* Product have only single variant (tested with only product template)
