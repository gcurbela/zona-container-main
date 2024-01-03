from odoo import fields, models, api


class SaleMakeInvoiceAdvance(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def _create_invoices(self, sale_orders):
        res = super(SaleMakeInvoiceAdvance, self)._create_invoices(sale_orders)
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        rouding_id = self.env['account.cash.rounding'].search([('predefinido_en_ventas','=',True)],limit=1)
        if rouding_id:
            for invoice_id in sale_orders.invoice_ids:
                invoice_id.invoice_cash_rounding_id = rouding_id.id

        return res



