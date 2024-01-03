from odoo import fields, models, api


class AccountCashRouding(models.Model):
    _inherit = 'account.cash.rounding'

    predefinido_en_ventas = fields.Boolean(string="Predefinido en Venta")


