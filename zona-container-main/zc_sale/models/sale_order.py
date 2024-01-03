from odoo import fields, models, api,_
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero
from odoo.addons.sale_subscription.models.sale_order import SaleOrder as OriginalSaleOrder

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    nro_identifiacion_order = fields.Char(string="Nº Identificación Compra")

    journal_id = fields.Many2one(
        "account.journal",
        string="Diario",
        domain="[('type', 'in', ['sale']), ('company_id', '=', company_id)]",
    )

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        if self.journal_id:
            res.update({
                "journal_id": self.journal_id.id,
            })
        return res

    def _create_invoices(self, grouped=False, final=False, date=None):
        res = super(SaleOrder, self)._create_invoices(grouped, final, date)
        rouding_id = self.env['account.cash.rounding'].search([('predefinido_en_ventas', '=', True)], limit=1)
        if self.nro_identifiacion_order:
            for invoice_id_nro in res:
                invoice_id_nro.nro_identifiacion = self.nro_identifiacion_order if self.nro_identifiacion_order else False
        if rouding_id:
            for invoice_id in res:
                invoice_id.invoice_cash_rounding_id = rouding_id.id
        return res

    def _get_invoiceable_lines(self, final=False):
        date_from = fields.Date.today()
        # res = super()._get_invoiceable_lines(final=final)
        # res = res.filtered(
        #    lambda l: l.temporal_type != 'subscription' or l.order_id.subscription_management == 'upsell')
        automatic_invoice = self.env.context.get('recurring_automatic')

        invoiceable_line_ids = []
        downpayment_line_ids = []
        pending_section = None

        for line in self.order_line:
            if line.display_type == 'line_section':
                # Only add section if one of its lines is invoiceable
                pending_section = line
                continue

            time_condition = line.order_id.next_invoice_date and line.order_id.next_invoice_date <= date_from and line.order_id.start_date and line.order_id.start_date <= date_from
            line_condition = time_condition or not automatic_invoice  # automatic mode force the invoice when line are not null
            line_to_invoice = False
            # if line in res:
            # Line was already marked as to be invoiced
            #    line_to_invoice = True

            if line.product_id.automatic_renewal:
                line_to_invoice = True

            elif line.order_id.subscription_management == 'upsell':
                # Super() already select everything that is needed for upsells
                line_to_invoice = False
            elif line.display_type or line.temporal_type != 'subscription':
                # Avoid invoicing section/notes or lines starting in the future or not starting at all
                line_to_invoice = False
            elif line_condition and line.product_id.invoice_policy == 'order' and line.order_id.state == 'sale':
                # Invoice due lines
                line_to_invoice = True
            elif line_condition and line.product_id.invoice_policy == 'delivery' and (
                    not float_is_zero(line.qty_delivered, precision_rounding=line.product_id.uom_id.rounding)):
                line_to_invoice = True
            if line_to_invoice:
                if line.is_downpayment:
                    # downpayment line must be kept at the end in its dedicated section
                    downpayment_line_ids.append(line.id)
                    continue
                if pending_section:
                    invoiceable_line_ids.append(pending_section.id)
                    pending_section = False
                invoiceable_line_ids.append(line.id)

        return self.env["sale.order.line"].browse(invoiceable_line_ids + downpayment_line_ids)

    OriginalSaleOrder._get_invoiceable_lines = _get_invoiceable_lines


    def _invoice_is_considered_free(self, invoiceable_lines):
        is_free, is_exception = super(SaleOrder, self)._invoice_is_considered_free(invoiceable_lines)

        is_free = False
        is_exception = False

        return is_free, is_exception


