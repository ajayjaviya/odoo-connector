# -*- coding: utf-8 -*-
from .common import MagentoInstanceTest


class TestMagentoImport(MagentoInstanceTest):
    def test_magento_import_store(self):
        """ Test the Magento Store Import
        """
        response = self.instance.import_store()
        store_count = self.env['magento.store'].search_count([('magento_store', '=', True)])
        self.assertTrue(store_count >= 1 and response.ok, 'Magento: Store import is wrong')

    def test_magento_import_category(self):
        """ Test the Magento Category Import
        """
        self.instance.import_store()
        response = self.instance.import_category()
        category_count = self.env['product.category'].search_count([('magento_id', '!=', False)])
        self.assertTrue(category_count >= 1 and response.ok, 'Magento: Category import is wrong')

    def test_magento_import_attribute_set(self):
        """ Test the Magento Attribute Set Import
        """
        self.instance.import_store()
        response = self.instance.import_attribute_set()
        category_count = self.env['magento.product.attribute.set'].search_count([])
        self.assertTrue(category_count >= 1 and response.ok, 'Magento: Category import is wrong')

    def test_magento_import_product(self):
        """ Test the Magento Product Import
        """
        self.instance.import_store()
        self.instance.import_attribute_set()
        self.instance.import_category()
        response = self.instance.import_products()
        product_count = self.env['product.template'].search_count([('magento_id', '!=', False)])
        self.assertTrue(response.ok, 'Magento: Product  Import  API is wrong')
        self.assertTrue(product_count >= 1, 'Magento: Product not found in magento')
