# -*- coding: utf-8 -*-
# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    cuenta_banc = fields.Char(string="Cuenta Bancaria")
    n_transaccion = fields.Char(string="Número de Transacción")
    adjunto_compro = fields.Binary(string="Comprobante")
    filename = fields.Char('file name')

    @api.multi
    def unlink(self):
        for rec in self:
            advances = self.env['tms.advance'].search(
                [('payment_move_id', '=', rec.id)])
            expenses = self.env['tms.expense'].search(
                [('payment_move_id', '=', rec.id)])
            loans = self.env['tms.expense.loan'].search(
                [('payment_move_id', '=', rec.id)])
            if advances:
                for advance in advances:
                    advance.paid = False
            if expenses:
                for expense in expenses:
                    expense.paid = False
            if loans:
                for loan in loans:
                    loan.paid = False
            return super(AccountMove, self).unlink()
