from odoo import fields, models, api
from io import StringIO
import xlwt
from datetime import datetime, timedelta
import platform
import base64
from odoo.exceptions import ValidationError


class ExcelReportSale(models.TransientModel):
    _name = 'excel.report.zc'
    _description = 'Reporte de ventas por contenedor'

    zc_report_data = fields.Char('Name', size=256)
    file_name = fields.Binary('Reporte Ventas ZC')

    start_date = fields.Date('Fecha inicio')
    end_date = fields.Date('Fecha fin')

    def validate_date_filters(self):
        if self.end_date and self.end_date < self.start_date:
            self.end_date = False
            raise ValidationError("La fecha final no puede ser menor a la fecha de inicio")

    def export_data(self):
        self.validate_date_filters()
        custom_value = {}
        label_lists = ['Numero de Contenedor', 'Tipo de Contenedor', 'Nombre Cliente', 'Numero de Factura', 'Fecha de Emisión', 'Importe Neto', 'Total']
        domain = [('create_date', '>=', self.start_date), ('create_date', '<=', self.end_date)]
        order = self.env['sale.order'].search(domain)
        workbook = xlwt.Workbook()
        s_no = 0
        sheet = workbook.add_sheet('Detalle de ventas')
        style0 = xlwt.easyxf(
            'font: name Times New Roman bold on;borders:left thin, right thin, top thin, bottom thin;align: horiz center;',
            num_format_str='#,##0.00')
        style1 = xlwt.easyxf(
            'font:bold True; borders:left thin, right thin, top thin, bottom thin;align: horiz center;',
            num_format_str='#,##0.00')

        sheet.write_merge(0, 0, 0, 0, 'Numero de contenedor', style1)
        sheet.write_merge(0, 0, 1, 2, 'Tipo de contenedor', style1)
        sheet.write_merge(0, 0, 3, 4, 'Cliente', style1)
        sheet.write_merge(0, 0, 5, 6, 'Numero de Factura', style1)
        sheet.write_merge(0, 0, 7, 8, 'Fecha de Emisión', style1)
        sheet.write_merge(0, 0, 9, 10, 'Importe Neto', style1)
        sheet.write_merge(0, 0, 11, 12, 'Total', style1)

        s_no = 1
        n = 0
        m = 0

        for rec in order:
            if rec.picking_ids:
                for pick in rec.picking_ids:
                    for mline in pick.move_line_ids.filtered(lambda l: l.lot_id.name != False and l.picking_id.state == 'done'):
                        custom_value['nro_contenedor'] = mline.lot_id.name
                        custom_value['tipo_contenedor'] = mline.product_id.name
                        custom_value['cliente'] = rec.partner_id.name
                        custom_value['numero_factura'] = rec.invoice_ids and rec.invoice_ids[0].number or ''
                        custom_value['fecha_emision'] = rec.invoice_ids and rec.invoice_ids[0].date_invoice or ''
                        custom_value['importe_neto'] = rec.amount_untaxed
                        custom_value['total'] = rec.amount_total

                        sheet.write_merge(n + 1, n + 1, m, m, custom_value['nro_contenedor'], style0)
                        sheet.write_merge(n + 1, n + 1, m + 1, m + 2, custom_value['tipo_contenedor'], style0)
                        sheet.write_merge(n + 1, n + 1, m + 3, m + 4, custom_value['cliente'], style0)
                        sheet.write_merge(n + 1, n + 1, m + 5, m + 6, custom_value['numero_factura'], style0)
                        sheet.write_merge(n + 1, n + 1, m + 7, m + 8, custom_value['fecha_emision'], style0)
                        sheet.write_merge(n + 1, n + 1, m + 9, m + 10, custom_value['importe_neto'], style0)
                        sheet.write_merge(n + 1, n + 1, m + 11, m + 12, custom_value['total'], style0)
                        s_no = s_no + 1
                        n += 1

        datas = []
        output = StringIO()
        label = ';'.join(label_lists)
        output.write(label)
        output.write("\n")

        for data in datas:
            record = ';'.join(data)
            output.write(record)
            output.write("\n")
        data = base64.b64encode(bytes(output.getvalue(), "utf-8"))

        if platform.system() == 'Linux':
            filename = ('/tmp/Reporte Ventas ZC' + '.xls')
        else:
            filename = ('Reporte Ventas ZC' + '.xls')

        workbook.save(filename)
        fp = open(filename, "rb")
        file_data = fp.read()
        out = base64.encodebytes(file_data)
        self.zc_report_data = 'Reporte Ventas ZC' + '.xls'
        self.file_name = out

        fp.close()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'excel.report.zc',
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'context': self.env.context,
            'target': 'new',
        }


