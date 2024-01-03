# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2023. All rights reserved.

from odoo import api, fields, models


class InvoiceApproval(models.Model):
    _name = 'invoice.approval'
    _order = 'id desc'

    name = fields.Char(string='Name', required=True)
    invoice_approver_ids = fields.One2many('invoice.approval.line', 'approval_id')


class InvoiceApprovers(models.Model):
    _name = 'invoice.approval.line'

    approval_id = fields.Many2one('invoice.approval', string='Approval', required=True)
    sequence = fields.Integer(string='Sequence', required=True)
    approver_id = fields.Many2one('res.users', string='Approver', required=True)
    is_required = fields.Boolean(default=False, string='Is Required')
