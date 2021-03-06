# -*- coding: utf-8 -*-
# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FleetVehicleLogFuelPrepaid(models.Model):
    _name = 'fleet.vehicle.log.fuel.prepaid'

    name = fields.Char()
    price_total = fields.Float(string='Total')
    invoice_id = fields.Many2one(
        'account.invoice', string='Invoice', readonly=True)
    invoice_paid = fields.Boolean(
        compute='_compute_invoiced_paid')
    operating_unit_id = fields.Many2one(
        'operating.unit', string='Operating Unit')
    notes = fields.Char()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('closet', 'Closet')],
        readonly=True,
        default='draft')
    vendor_id = fields.Many2one('res.partner', string="Supplier")
    date = fields.Date(
        required=True,
        default=fields.Date.context_today)
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        domain=[('tms_product_category', '=', 'fuel')])
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        required=True,
        default=lambda self: self.env.user.company_id.currency_id)
    log_fuel_ids = fields.One2many(
        'fleet.vehicle.log.fuel',
        'prepaid_id',
        string='Fuel Vauchers',
        readonly=True,
    )
    balance = fields.Float()

    @api.model
    def create(self, values):
        res = super(FleetVehicleLogFuelPrepaid, self).create(values)
        if not res.operating_unit_id.prepaid_fuel_sequence_id:
            raise ValidationError(_(
                'You need to define the sequence for fuel logs in base %s' %
                res.operating_unit_id.name
            ))
        sequence = res.operating_unit_id.prepaid_fuel_sequence_id
        res.name = sequence.next_by_id()
        return res

    # @api.multi
    # @api.depends('log_fuel_ids')
    # def _compute_balance(self):
        # for rec in self:
        #     rec.balance = rec.price_total
        #     for fuel in rec.log_fuel_ids:
        #         rec.balance -= fuel.price_total
        #         if rec.balance > rec.price_total:
        #             raise ValidationError(
        #                 _('The total amount of fuel voucher is '
        #                   'higher than the allowed limit'))

    @api.depends('invoice_id')
    def _compute_invoiced_paid(self):
        for rec in self:
            if rec.invoice_id and rec.invoice_id.state == "paid":
                rec.invoice_paid = True

    @api.multi
    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    @api.multi
    def create_invoice(self):
        for rec in self:
            obj_invoice = self.env['account.invoice']
            if rec.invoice_id:
                raise ValidationError(
                    _('The record is already invoiced'))
            journal_id = rec.operating_unit_id.purchase_journal_id.id
            fpos = rec.vendor_id.property_account_position_id
            invoice_account = fpos.map_account(
                rec.vendor_id.property_account_payable_id)
            if rec.product_id.property_account_income_id:
                account = fpos.map_account(
                    rec.product_id.property_account_income_id)
            elif (rec.product_id.categ_id.
                    property_account_income_categ_id):
                account = fpos.map_account(
                    rec.product_id.categ_id.
                    property_account_income_categ_id)
            else:
                raise ValidationError(
                    _('You must have an income account in the '
                      'product or its category.'))
            invoice_id = obj_invoice.create({
                'partner_id': rec.vendor_id.id,
                'operating_unit_id': rec.operating_unit_id.id,
                'fiscal_position_id': fpos.id,
                'journal_id': journal_id,
                'currency_id': rec.currency_id.id,
                'account_id': invoice_account.id,
                'type': 'in_invoice',
                'invoice_line_ids': [(0, 0, {
                    'product_id': rec.product_id.id,
                    'quantity': 1,
                    'price_unit': rec.price_total,
                    'uom_id': rec.product_id.uom_id.id,
                    'name': rec.name,
                    'account_id': account.id,
                })]
            })
            rec.write({'invoice_id': invoice_id.id})
            message = _(
                '<strong>Invoice of:</strong> %s </br>') % (rec.name)
            invoice_id.message_post(body=message)

            return {
                'name': 'Customer Invoice',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'current',
                'res_model': 'account.invoice',
                'res_id': invoice_id.id,
                'type': 'ir.actions.act_window'
            }
