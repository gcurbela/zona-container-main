# -*- coding: utf-8 -*-

from odoo import models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    def write(self, values):
        res = super(AccountMove, self).write(values)
        if "journal_id" in values:
            for line in self.invoice_line_ids:
                account = line._get_move_line_account(self, line.product_id)
                if account and line.account_id != account:
                    line.write({
                        "account_id": account.id
                    })
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def _get_move_line_account(self, move_id, product_id):
        journal_id = move_id.journal_id
        if move_id.move_type in ("out_invoice", "out_refund"):
            account_id = (
                product_id.property_account_income_id or
                product_id.categ_id.property_account_income_categ_id or
                journal_id.default_account_id
            )
        else:
            account_id = (
                product_id.property_account_expense_id or
                product_id.categ_id.property_account_expense_categ_id or
                journal_id.default_account_id
            )
        return account_id

    def write(self, vals):
        res = super(AccountMoveLine, self).write(vals)
        for rec in self:
            if vals.get('product_id'):
                account = self._get_move_line_account(rec.move_id, rec.product_id)
                if account:
                    rec.account_id = account
        return res

    @api.model_create_multi
    def create(self, vals):
        for val in vals:
            if val.get('product_id') and 'exclude_from_invoice_tab' in val.keys() and not val.get('exclude_from_invoice_tab'):
                move = self.env["account.move"].browse(val["move_id"])
                product = self.env["product.product"].browse(val["product_id"])
                account_id = self._get_move_line_account(move, product)
                if account_id:
                    val["account_id"] = account_id.id
        return super(AccountMoveLine, self).create(vals)
