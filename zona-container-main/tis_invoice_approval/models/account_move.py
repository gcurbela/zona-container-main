# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2023. All rights reserved.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_approval = fields.Boolean(compute='compute_is_approval')
    is_validated = fields.Boolean(compute='compute_is_validated', default=True)
    hide_approve_button = fields.Boolean(compute='compute_hide_approve_button', default=False)
    approver_validate_ids = fields.One2many('invoice.approval.validate', 'move_id', readonly=True)

    @api.depends('approver_validate_ids')
    def compute_hide_approve_button(self):
        for rec in self:
            if self.env.user.id not in rec.approver_validate_ids.mapped('approver_id').ids:
                rec.hide_approve_button = True
            else:
                rec.hide_approve_button = False

    def compute_is_approval(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        is_approval = ICPSudo.get_param('tis_invoice_approval.approvals')
        for rec in self:
            rec.is_approval = True if is_approval else False

    def compute_is_validated(self):
        for rec in self:
            approval_line = self.approver_validate_ids.filtered(
                lambda l: l.approver_id.id == self.env.user.id and l.is_validated == True)
            rec.is_validated = True if approval_line or not rec.approver_validate_ids else False

    @api.model
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        if res.is_approval:
            approval = self.env['invoice.approval'].search([], order='id desc', limit=1)
            approval_lines = approval.invoice_approver_ids.search(
                [('is_required', '=', True), ('approval_id', '=', approval.id)], order='sequence')
            flag = 0
            for line in approval_lines:
                res.approver_validate_ids = [
                    (0, 0, {'move_id': res.id, 'approver_id': line.approver_id.id, 'is_validated': False})]
                if flag == 0:
                    self.send_approval_mail_notification(approver=line.approver_id)
                    flag = 1
        return res

    def button_approve(self):
        if not self.invoice_line_ids:
            raise UserError('You need to add a line before approving.')
        user = self.env.user
        user_line = self.approver_validate_ids.search([('is_validated', '=', False), ('move_id', '=', self.id)],
                                                      order='id asc', limit=1)
        if user.id == user_line.approver_id.id:
            user_line.is_validated = True
            next_approver = self.approver_validate_ids.search([('is_validated', '=', False), ('move_id', '=', self.id)],
                                                              order='id asc', limit=1)
            self.send_approval_mail_notification(approver=next_approver.approver_id)
            self.message_post(body=_('Approved this invoice'))
            self.action_post()

        else:
            raise UserError('Other approvals pending.')

    def send_approval_mail_notification(self, approver):
        template_id = self.env['ir.model.data']._xmlid_to_res_id(
            'tis_invoice_approval.mail_notification_approval',
            raise_if_not_found=False)
        if not template_id:
            return
        values = {
            'object': self,
            'access_link': self._notify_get_action_link('view'),
            'company': self.env.company,
        }
        if approver:
            values.update(assignee_name=approver.sudo().name)
            assignation_msg = self.env['ir.ui.view']._render_template('tis_invoice_approval.mail_notification_approval',
                                                                      values)
            assignation_msg = self.env['mail.render.mixin']._replace_local_links(assignation_msg)
            self.env["mail.mail"].sudo().create(
                {
                    "email_from": self.create_uid.email,
                    "body_html": assignation_msg,
                    "subject": _('Approval Required'),
                    "email_to": approver.email,
                    "auto_delete": True,
                }
            ).sudo().send()


    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft=soft)
        if res.is_approval:
            for invoice in res:
                if invoice.move_type == 'out_refund':
                    user_line = invoice.approver_validate_ids.search([('is_validated', '=', False), ('move_id', '=', invoice.id)])
                    if user_line:
                        raise UserError('La factura está pendiente de aprobar..')
        return res


class InvoiceApprovalValidate(models.Model):
    _name = 'invoice.approval.validate'

    move_id = fields.Many2one('account.move', required=True)
    approver_id = fields.Many2one('res.users')
    is_validated = fields.Boolean(default=False, string='Approved')
