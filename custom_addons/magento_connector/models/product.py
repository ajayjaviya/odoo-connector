# -*- coding: utf-8 -*-
import base64
import json
from urllib.request import urlopen
from odoo import models , fields,api,_


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    magento_id = fields.Char(string='Magento ID')

    @api.multi
    def _get_default_store(self):
        '''set first store as default store for product'''
        return self.env['magento.store'].search([], limit=1).id

    magento_store_id = fields.Many2one('magento.store', string="Magento Store", default=_get_default_store)
    product_type = fields.Selection([('simple', 'Simple Product'),
                     ('configurable', 'Configurable Product'),
                     ('grouped', 'Grouped Product'),
                     ('virtual', 'Virtual Product'),
                     ('bundle', 'Bundle Product'),
                     ('mygrouped', 'My Grouped'),
                     ('downloadable', 'Downloadable Product')]
                    , 'Type', default='simple')

    sync_with_mangento = fields.Boolean(readonly=1)

    @api.multi
    def sync_product(self, instance, sku):
        ProductTemplate = self.env['product.template']
        response = instance.magento_api("/rest/V1/products/%s" % sku)
        products_data = json.loads(response.text)
        vals = {
            'name': products_data.get('name'),
            'default_code': sku,
            'product_type': products_data.get('type_id'),
            'list_price': products_data.get('price'),
            'weight': products_data.get('weight'),
            'type': 'product'
        }
        # Map Product Category
        if products_data.get('extension_attributes'):
            if products_data['extension_attributes'].get('category_links'):
                magento_category_id = products_data['extension_attributes']['category_links'][0].get('category_id')
                if magento_category_id:
                    category = self.env['product.category'].search([('magento_id', '=', magento_category_id)])
                    if category:
                        vals.update({
                            'categ_id': category.id
                        })
        # Import Product Image
        if products_data.get('media_gallery_entries'):
            file = products_data['media_gallery_entries'][0].get('file')
            if file:
                image = ProductTemplate.get_magento_image(instance.location , file)
                vals.update({
                    'image': image
                })
        product = ProductTemplate.search([('default_code', '=', sku)])
        if product:
            product.write(vals)
        else:
            product = ProductTemplate.create(vals)
        # Update Stock
        if products_data['extension_attributes'].get('stock_item') and products_data['extension_attributes']['stock_item'].get('qty'):
            variant = self.env['product.product'].search([('product_tmpl_id', '=', product.id)])
            variant.sync_product_stock(products_data['extension_attributes']['stock_item']['qty'])
        return product

    @api.multi
    def get_magento_image(self, location, file):
        url = "%s%s%s" % (location, 'pub/media/catalog/product', file)
        file_contain = urlopen(url).read()
        image = base64.encodestring(file_contain)
        return image

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def sync_product_stock(self, qty):
        '''Sync Product Stock form magento to odoo'''
        inventory_wizard = self.env['stock.change.product.qty'].create({
            'product_id': self.id,
            'new_quantity': qty,
        })
        return inventory_wizard.change_product_qty()

    @api.multi
    def export_product(self):
        instance = self.magento_store_id.magento_instance_id
        custom_options = []
        categ = [category.magento_id for category in self.categ_id  if category.magento_id]
        if categ:
            custom_options.append({"attributeCode": 'category_ids', "value": categ})
        vals = {
            "product": {
                "id": 0,
                "sku": str(self.default_code),
                "name": str(self.name),
                "price": self.list_price,
                "type_id": self.product_type,
                "customAttributes": custom_options,
                'attribute_set_id': 1,
                'weight': 0.5,
                'status': '1',
                'visibility':'4',
                'tax_class_id': 0,
                'description': str(self.name),
                'short_description': str(self.name),
            }
        }
        url = "%s%s%s" % ("rest/" , self.magento_store_id.code , "/V1/products/")
        response = instance.magento_api(url, 'POST', vals)
        import pdb;pdb.set_trace()
        print('----------------->>>', response)
        if str(response.status_code) == "200":
            print('----------------->>> Text' , response.text)
            # data = json.loads(response.text)
            self.write({'sync_with_mangento': True})
        return True

class ProductCategory(models.Model):
    _inherit = 'product.category'

    magento_id = fields.Integer('Code')
    shop_id = fields.Many2one('magento.store', 'shop')

    position = fields.Integer('Position')
    level = fields.Integer('Level')
    magento_instance_id = fields.Many2one('magento.instance', string='Magento Instance')