# -*- coding: utf-8 -*-
import base64
import codecs
import io
import json
from PIL import Image

from odoo import models, fields, api, _
from odoo.tools.mimetypes import guess_mimetype
from urllib.request import urlopen


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
    attribute_set_id = fields.Many2one('magento.product.attribute.set', 'Attribute Set')
    visibility = fields.Selection([('1', 'Not Visible Individually'),
                                   ('2', 'Catalog'),
                                   ('3', 'Search'),
                                   ('4', 'Catalog, Search'),
                                   ], 'Visibility', default='1')
    magento_product_status = fields.Selection([('1', 'Enabled'), ('2', 'Disabled')], 'Status', default='1')
    is_magento_product = fields.Boolean()
    # Magento Sync Status is used to identified the next operation to do
    magento_sync_status = fields.Selection([('to_export', 'To Export'), ('to_update', 'To Update'), ('exported', 'Exported'), ('updated', 'Updated'), ('imported', 'Imported')], default="to_export")

    @api.multi
    def sync_product(self, instance, sku):
        """ Create Product in Odoo"""
        ProductTemplate = self.env['product.template']
        response = instance.magento_api("/rest/V1/products/%s" % sku)
        products_data = json.loads(response.text)
        attribute = self.env['magento.product.attribute.set'].search(
            [('code', '=', products_data.get('attribute_set_id'))], limit=1)

        vals = {
            'name': products_data.get('name'),
            'default_code': sku,
            'product_type': products_data.get('type_id'),
            'list_price': products_data.get('price'),
            'weight': products_data.get('weight'),
            'type': 'product',
            'attribute_set_id': attribute.id,
            'visibility': str(products_data.get('visibility')),
            'magento_product_status': str(products_data.get('status')),
            'magento_sync_status': 'imported'
        }
        # Map Product Category
        if products_data.get('extension_attributes'):
            if products_data['extension_attributes'].get('category_links'):
                magento_category_id = products_data['extension_attributes']['category_links'][0].get('category_id')
                if magento_category_id:
                    category = self.env['product.category'].search([('magento_id', '=', magento_category_id)], limit=1)
                    if category:
                        vals.update({
                            'categ_id': category.id
                        })
        # Import Product Image
        if products_data.get('media_gallery_entries'):
            file = products_data['media_gallery_entries'][0].get('file')
            if file:
                image = ProductTemplate.get_magento_image(instance.location, file)
                vals.update({
                    'image': image
                })
        product = ProductTemplate.search([('default_code', '=', sku)])
        if product:
            product.write(vals)
        else:
            product = ProductTemplate.create(vals)
        # Update Stock
        if products_data['extension_attributes'].get('stock_item') and products_data['extension_attributes'][
            'stock_item'].get('qty'):
            variant = self.env['product.product'].search([('product_tmpl_id', '=', product.id)])
            variant.sync_product_stock(products_data['extension_attributes']['stock_item']['qty'])
        return product

    @api.multi
    def get_magento_image(self, location, file):
        """ Import Image (Media) from Magento."""
        url = "%s%s%s" % (location, '/pub/media/catalog/product', file)
        file_contain = urlopen(url).read()
        image = base64.encodestring(file_contain)
        return image

    @api.multi
    def _cron_export_product_magento(self):
        """ Export newly created product in odoo to Magento using cron"""
        products = self.env['product.product'].search([('magento_sync_status', '=', 'to_export')])
        for product in products:
            res = product.export_product()
            if res and product.sync_with_mangento:
                product.product_tmpl_id.magento_sync_status = 'exported'

    @api.multi
    def _cron_update_product_magento(self):
        """ Update product to Magento using cron"""
        products = self.env['product.product'].search([('magento_sync_status', '=', 'to_update')])
        for product in products:
            res = product.update_product()
            if res and product.sync_with_mangento:
                product.product_tmpl_id.magento_sync_status = 'updated'

    @api.multi
    def write(self, vals):
        """ When product is update in odoo status is changed to To Update it will usefull
        for cron to which product need to update on Magento too"""
        if 'magento_sync_status' not in vals:
            vals.update({
                'magento_sync_status': 'to_update'
            })

        return super(ProductTemplate, self).write(vals)

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
    def update_product(self):
        """"Update Product to Magento
        """
        instance = self.magento_store_id.magento_instance_id
        custom_options = []
        categ = [category.magento_id for category in self.categ_id if category.magento_id]
        if categ:
            custom_options.append({"attributeCode": 'category_ids', "value": categ})
        vals = {
            "product": {
            "name": str(self.name),
            "price": self.list_price,
            'weight': self.weight,
            'status': int(self.magento_product_status),
            'visibility': int(self.visibility),
            }
        }
        url = "%s%s" % ("/rest/V1/products/", self.default_code)
        response = instance.magento_api(url, 'PUT', vals)
        if str(response.status_code) == "200":
            data = json.loads(response.text)
            # Sync Product Stock
            if self.qty_available:
                self.export_product_stock(instance)
            if self.image:
                self.export_product_image(instance)
            self.write({'sync_with_mangento': True, 'magento_id': data.get('id')})
        return True

    @api.multi
    def export_product(self):
        """"Export Product to Magento
        """
        instance = self.magento_store_id.magento_instance_id
        custom_options = []
        categ = [category.magento_id for category in self.categ_id if category.magento_id]
        if categ:
            custom_options.append({"attributeCode": 'category_ids', "value": categ})
        vals = {
            "product": {
                "id": 0,
                "sku": str(self.default_code),
                "name": str(self.name),
                "price": self.list_price,
                "type_id": str(self.product_type),
                "customAttributes": custom_options,
                'attributeSetId': self.attribute_set_id.id or 4,
                'weight': self.weight,
                'status': int(self.magento_product_status),
                'visibility': int(self.visibility),
            }
        }
        url = "%s%s%s" % ("/rest/", self.magento_store_id.code, "/V1/products/")
        response = instance.magento_api(url, 'POST', vals)
        if str(response.status_code) == "200":
            data = json.loads(response.text)
            # Sync Product Stock
            if self.qty_available:
                self.export_product_stock(instance)
            if self.image:
                self.export_product_image(instance)
            self.write({'sync_with_mangento': True, 'magento_id': data.get('id')})
        return response

    @api.multi
    def export_product_stock(self, instance):
        """"Export Product Stock to Magento"""
        vals = {"stockItem": {"qty": self.qty_available}}
        url = "%s%s%s" % ("/rest/V1/products/", self.default_code, "/stockItems/1")
        return instance.magento_api(url, 'PUT', vals)

    @api.multi
    def export_product_image(self, instance):
        """"Export Product Image to Magento"""
        image_stream = io.BytesIO(codecs.decode(self.image, 'base64'))
        image = Image.open(image_stream)

        filename = image.filename or ("%s.%s") % (self.default_code, image.format.lower())
        vals = {
            "entry": {
                "mediaType": "image",
                "label": filename,
                "disabled": "false",
                "types": [
                    "image",
                    "small_image",
                    "thumbnail"
                ],
                "file": "string",
                "content": {
                    "base64_encoded_data": self.image.decode("utf-8"),
                    "type": guess_mimetype(base64.b64decode(self.image)),
                    "name": filename
                }
            }
        }
        url = "%s%s%s" % ("/rest/V1/products/", self.default_code, "/media")
        response = instance.magento_api(url, 'POST', vals)
        return response

class ProductCategory(models.Model):
    _inherit = 'product.category'

    magento_id = fields.Integer('Code')
    shop_id = fields.Many2one('magento.store', 'shop')

    position = fields.Integer('Position')
    level = fields.Integer('Level')
    magento_instance_id = fields.Many2one('magento.instance', string='Magento Instance')