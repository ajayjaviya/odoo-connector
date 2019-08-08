# -*- coding: utf-8 -*-
import json
import logging

import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class MagentoInstance(models.Model):
    _name = 'magento.instance'
    _description = 'Magento Instance'

    name = fields.Char(string='Name', required=True)
    location = fields.Char(string='Location', required=True)
    access_token = fields.Char(string='Access Token', required=True)
    stock_location_id = fields.Many2one('stock.location',
                                        string='Stock Location')

    def magento_api(self, url, method="GET", vals=None):
        url = '%s%s' % (self.location, url)
        headers = {'authorization': 'Bearer %s' % self.access_token}
        if method == 'POST':
            response = requests.request(method, url, data=json.dumps(vals), headers=headers)
        else:
            response = requests.request(method, url, headers=headers)
        return response

    @api.multi
    def import_store(self):
        response = self.magento_api('/rest/V1/store/storeViews')
        if response.ok:
            stores = json.loads(response.text)
            for store in stores:
                if len(store) and store.get('name') != 'Admin':
                    self.env['magento.store'].create({
                        'name': store['name'],
                        'code': store['code'],
                        'store_id': store['id'],
                        'website_id': store['website_id'],
                        'magento_shop': True,
                        'magento_instance_id': self.id,
                    })

                self._cr.commit()

    @api.multi
    def create_parent_category(self, shop, data):
        ProductCatgory = self.env['product.category']
        category = ProductCatgory.search([('name', '=', data.get('name')), ('magento_id', '=', data.get('id')),
                                          ('magento_instance_id', '=', self.id)])
        if not category:
            ProductCatgory.create({
                'magento_id': data.get('id'),
                'magento_instance_id': self.id,
                'position': data.get('position'),
                'level': data.get('Level'),
                'name': data.get('name'),
                'shop_id': shop.id,
            })

    @api.multi
    def create_sub_category(self, shop, data):
        ProductCatgory = self.env['product.category']
        sub_categ_id = ProductCatgory.search([('magento_id', '=', data['id']), ('name', '=', data['name']),
                                              ('magento_instance_id', '=', self.id)])
        if not sub_categ_id:
            categ_id = ProductCatgory.search([('magento_id', '=', data['parent_id']), ('magento_instance_id', '=',
                                                                                       self.id)])
            if categ_id:
                ProductCatgory.create({
                    'parent_id': categ_id.id,
                    'magento_id': data['id'],
                    'name': data['name'],
                    'magento_instance_id': self.id,
                    'position': data['position'],
                    'level': data['level'],
                    'shop_id': shop.id,
                })

    @api.multi
    def import_attribute_set(self):
        MagentoProductAttributeSet = self.env['magento.product.attribute.set']
        response = self.magento_api("rest/V1/products/attribute-sets/sets/list?searchCriteria=0")
        stores = self.env['magento.store'].search([])
        if response.ok:
            for store in stores:
                attributes = response.json().get('items')
                for attribute in attributes:
                    val = {
                        'name': attribute['attribute_set_name'],
                        'code': attribute['attribute_set_id'],
                        'shop_id': store.id,
                        'sort_order': attribute['sort_order'],
                        'entity_type_id': attribute['entity_type_id'],
                        'magento_instance_id': self.id,
                    }
                    attribute_set = MagentoProductAttributeSet.search(
                        [('name', '=', attribute['attribute_set_name']), ('magento_instance_id', '=', self.id)])
                    if attribute_set:
                        attribute_set.write(val)
                    else:
                        MagentoProductAttributeSet.create(val)
        return True

    @api.multi
    def import_category(self):
        try:
            shops = self.env['magento.store'].search([('magento_instance_id', '=', self.id)])
            if not shops:
                raise UserError(_('Please Create Store'))
            response = self.magento_api('/rest/V1/categories')
            if response.ok:
                categories_data = response.json()
                for shop in shops:
                    if categories_data.get('is_active'):
                        if str(categories_data.get('parent_id')) == '1' or str(categories_data.get('parent_id')) == '0':
                            self.create_parent_category(shop, categories_data)
                        if len(categories_data.get('children_data')):
                            sub_categ = categories_data.get('children_data')
                            for categ in sub_categ:
                                self.create_sub_category(shop, categ)
                                for sub_in_sub in categ['children_data']:
                                    self.create_sub_category(shop, sub_in_sub)
                                    if sub_in_sub['children_data']:
                                        for sub_to_sub in sub_in_sub['children_data']:
                                            self.create_sub_category(shop, sub_to_sub)
                                            if sub_to_sub['children_data']:
                                                for sub_cat in sub_to_sub['children_data']:
                                                    self.create_sub_category(shop, sub_cat)
        except Exception:
            pass
        return True

    @api.multi
    def import_products(self):
        ProductTemplate = self.env['product.template']
        response = self.magento_api("/rest/V1/products?searchCriteria[filterGroups][0][filters][0][field]=type_id& searchCriteria[filterGroups][0][filters][0][value]=simple& searchCriteria[filterGroups][0][filters][0][conditionType]=eq")
        product_list = json.loads(response.text)
        for products in product_list['items']:
            ProductTemplate.sync_product(self, products['sku'])
        return True

    @api.multi
    def export_products(self):
        products = self.env['product.product'].search([('type', '=', 'product')])
        for product in products:
            product.export_product()
        return True