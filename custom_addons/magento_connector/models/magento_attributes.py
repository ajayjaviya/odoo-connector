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


class MagentoProductAttributes(models.Model):
    _name = "magento.product.attributes"
    _description = "Attributes of products"
    _rec_name = "attribute_code"

    attribute_code = fields.Char('Code')
    magento_id = fields.Char('ID')
    set_id = fields.Integer('Attribute Set')
    options = fields.One2many('magento.product.attribute.options', 'attribute_id', 'Attribute Options')
    frontend_input = fields.Selection([
        ('text', 'Text'),
        ('textarea', 'Text Area'),
        ('select', 'Selection'),
        ('multiselect', 'Multi-Selection'),
        ('boolean', 'Yes/No'),
        ('date', 'Date'),
        ('price', 'Price'),
        ('weight', 'Weight'),
        ('media_image', 'Media Image'),
        ('gallery', 'Gallery'),
        ('weee', 'Fixed Product Tax'),
        ('None', 'None'),
        # this option is not a magento native field it will be better to found a generic solutionto manage this kind of custom option
    ], 'Frontend Input'
    )
    frontend_input_id = fields.Many2one('frontend.input', string='Frontend Input')
    frontend_class = fields.Char('Frontend Class')
    backend_model = fields.Char('Backend Model')
    backend_type = fields.Selection([
        ('static', 'Static'),
        ('varchar', 'Varchar'),
        ('text', 'Text'),
        ('decimal', 'Decimal'),
        ('int', 'Integer'),
        ('datetime', 'Datetime')], 'Backend Type')
    scope = fields.Selection([
        ('store', 'Store View'),
        ('website', 'Website'),
        ('global', 'Global')], 'Scope')
    frontend_label = fields.Char('Label')
    is_visible_in_advanced_search = fields.Boolean('Visible in advanced search?')
    is_global = fields.Boolean('Global ?')
    is_filterable = fields.Boolean('Filterable?')
    is_comparable = fields.Boolean('Comparable?')
    is_visible = fields.Boolean('Visible?')
    is_searchable = fields.Boolean('Searchable ?')
    is_user_defined = fields.Boolean('User Defined?')
    is_configurable = fields.Boolean('Configurable?')
    is_visible_on_front = fields.Boolean('Visible (Front)?')
    is_used_for_price_rules = fields.Boolean('Used for pricing rules?')
    is_unique = fields.Boolean('Unique?')
    is_required = fields.Boolean('Required?')
    position = fields.Integer('Position')
    group_id = fields.Integer('Group')
    group = fields.Many2one('magento.product.attribute.groups', 'Attribute Group', readonly=True)
    apply_to = fields.Char('Apply to')
    default_value = fields.Char('Default Value')
    note = fields.Char('Note')
    entity_type_id = fields.Integer('Entity Type')
    referential_id = fields.Many2one('magento.instance', 'Magento Instance', readonly=True)
    field_name = fields.Char('Open ERP Field name')
    attribute_set_info = fields.Text('Attribute Set Information')
    based_on = fields.Selection([('product_product', 'Product Product'), ('product_template', 'Product Template')],
                                'Based On')


class MagentoProductAttributeGroups(models.Model):
    _name = "magento.product.attribute.groups"
    _description = "Attribute groups in Magento"
    _rec_name = 'attribute_group_name'
    _order = "sort_order"

    attribute_set_id = fields.Integer('Attribute Set ID')
    attribute_set = fields.Many2one("magento.product.attribute.set", "Attribute Set")
    attribute_group_name = fields.Char('Group Name')
    sort_order = fields.Integer('Sort Order')
    default_id = fields.Integer('Default')
    referential_id = fields.Many2one('magento.instance', 'Magento Instance', readonly=True)


class MagentoProductAttributeOptions(models.Model):
    _name = "magento.product.attribute.options"
    _description = "Options  of selected attributes"
    _rec_name = "label"

    attribute_id = fields.Many2one('magento.product.attributes', 'Attribute')
    attribute_name = fields.Char(related='attribute_id.attribute_code', type='char', string='Attribute Code', )
    value = fields.Char('Value')
    ipcast = fields.Char('Type cast')
    label = fields.Char('Label')
    referential_id = fields.Many2one('magento.instance', 'Magento Instance')
    product_id = fields.Many2one('product.template', 'Product')
    attri_id = fields.Many2one('magento.instance', 'Attributes')
    product_temp_id = fields.Many2one('product.product', 'Product')


class FrontendInput(models.Model):
    _name = "frontend.input"
    _description = "Frontend Input type"
    _rec_name = "name_type"

    name_type = fields.Char(string='Name')