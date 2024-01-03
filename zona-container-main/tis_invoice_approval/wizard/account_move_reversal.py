# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    def _prepare_default_reversal(self, move):
        res = super()._prepare_default_reversal(move)
        if move.is_approval:
            res.update({
                'auto_post': 'monthly',
            })
        return res
