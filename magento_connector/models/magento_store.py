# -*- coding: utf-8 -*-
import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class MagentoStore(models.Model):
    _name = 'magento.store'
    _description = "Magento Store"

    name = fields.Char(required=True, readonly=True)
    magento_store = fields.Boolean(string='Magento Store', readonly=True)
    store_id = fields.Integer(string='Store ID')
    prefix = fields.Char(string='Prefix', default='magento_')
    code = fields.Char(string='Code', readonly=True)
    stock_location_id = fields.Many2one('stock.location', string='Stock Location')
    magento_instance_id = fields.Many2one('magento.instance', string='Instance')
