# -*- coding: utf-8 -*-
from .common import MagentoInstanceTest

class TestMagentoExport(MagentoInstanceTest):
    def test_magento_export_product(self):
        self.uom_unit = self.env.ref('product.product_uom_unit')
        ProductTempalate = self.env['product.template']
        ProductTempalate.create({
            'name': 'Laptop',
            'uom_id': self.uom_unit.id,
            'default_code': 'HP-LP-01',
            'price': 100,
            'product_type': 'simple',
            'weight': 0.5,
            'magento_product_status': '1',
            'visibility': '2',
        })
        product = self.env['product.product'].search([('magento_sync_status', '=', 'to_update')])
        response = product.export_product()
        self.assertEqual(response.status_code, 200, 'Magento: Product is not export')
