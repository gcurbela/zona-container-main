from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    automatic_renewal = fields.Boolean(string="Renovación Automática", default=True)
