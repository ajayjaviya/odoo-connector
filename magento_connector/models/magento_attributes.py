# -*- coding: utf-8 -*-
from odoo import fields, api, models, _

class MagentoProductAttributeSet(models.Model):
    _name = "magento.product.attribute.set"

    name = fields.Char(string='Attribute Set Name', required=True)
    code = fields.Integer(string='Code', required=True)
    shop_id = fields.Many2one('magento.store', string='shop')
    sort_order = fields.Integer(string='sort Order')
    entity_type_id = fields.Integer(string='Entity Type')
    magento_instance_id = fields.Many2one('magento.instance', string='Magento Instance')