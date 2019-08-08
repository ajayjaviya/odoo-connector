from odoo import models , fields,api,_

class product_category(models.Model):
    _inherit = 'product.category'

    magento_id = fields.Integer('Code')
    shop_id = fields.Many2one('magento.store', 'shop')

    position = fields.Integer('Position')
    level = fields.Integer('Level')
    magento_instance_id = fields.Many2one('magento.instance', string='Magento Instance')