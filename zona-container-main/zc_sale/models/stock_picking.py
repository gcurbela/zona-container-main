from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super().button_validate()
        for rec in self:
            if rec.sale_id:
                for order_line in rec.move_line_ids:
                    stock_quant = self.env['stock.quant'].search([('lot_id','=',order_line.lot_id.id), ('product_id','=',order_line.product_id.id), ('inventory_quantity_set','=',True)])
                    stock_quant_product_name = []
                    if stock_quant:
                        for prod in stock_quant:
                            stock_quant_product_name.append(prod.display_name)
                        raise ValidationError("Hay productos sin aplicar el ajuste de inventario: " + str(stock_quant_product_name))
                    body = _('El contenedor %s fue entregado al cliente %s', order_line.lot_id.name, rec.partner_id.name)
                    rec.sale_id.message_post(body=body)
        return res




