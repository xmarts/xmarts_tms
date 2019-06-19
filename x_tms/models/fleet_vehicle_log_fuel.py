# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from __future__ import division

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
try:
    from num2words import num2words
except ImportError:
    _logger.debug('Cannot `import num2words`.')


class FleetVehicleLogFuel(models.Model):
    _name = 'fleet.vehicle.log.fuel'
    _inherit = ['fleet.vehicle.log.fuel', 'mail.thread', 'ir.needaction_mixin']
    _order = "date desc,vehicle_id desc"

    name = fields.Char()
    travel_id = fields.Many2one('tms.travel', string='Travel')
    
    expense_id = fields.Many2one('tms.expense', string='Expense')
    employee_id = fields.Many2one(
        'hr.employee',
        string='Driver',
        domain=[('driver', '=', True)],
        compute='_compute_employee_id',
        store=True,)
    odometer = fields.Float(related='vehicle_id.odometer',)
    product_uom_id = fields.Many2one('product.uom', string='UoM')
    product_qty = fields.Float(string='Liters', default=1.0,)
    tax_amount = fields.Float(string='Taxes',compute="_compute_taxes")
    price_total = fields.Float(string='Total', compute="_compute_total", store=True)
    special_tax_amount = fields.Float(
        compute="_compute_special_tax_amount", string='IEPS')
    price_unit = fields.Float(
        compute='_compute_price_unit', string='Unit Price')
    price_subtotal = fields.Float(
        string="Subtotal", compute='_compute_price_subtotal')
    invoice_id = fields.Many2one(
        'account.invoice', string='Invoice', readonly=True)
    invoice_paid = fields.Boolean(
        compute='_compute_invoiced_paid')
    operating_unit_id = fields.Many2one(
        'operating.unit', string='Operating Unit',default=lambda self: self.env['operating.unit'].search([('name','=','Mexico')], limit=1).id or self.env['operating.unit'].search([('name','=','México')], limit=1).id or '')
    notes = fields.Char()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('confirmed', 'Confirmed'),
        ('closed', 'Closed'),
        ('cancel', 'Cancelled')],
        readonly=True,
        default='draft')
    vendor_id = fields.Many2one('res.partner')
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        domain=[('tms_product_category', '=', 'fuel')])
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        required=True,
        default=lambda self: self.env.user.company_id.currency_id)
    expense_control = fields.Boolean(readonly=True)
    ticket_number = fields.Char()
    prepaid_id = fields.Many2one(
        'fleet.vehicle.log.fuel.prepaid',
        string='Prepaid'
    )
    tax_amount2 = fields.Float(string='Taxes',compute="_compute_taxes2")
    price_total2 = fields.Float(string='Total', compute="_compute_total2")
    price_subtotal2 = fields.Float(
        string="Subtotal", compute='_compute_price_subtotal2')

    # @api.model
    # def default_get(self, default_fields):
    #     res = super(FleetVehicleLogFuel, self).default_get(default_fields)
    #     service = self.env.ref('fleet.type_service_refueling', raise_if_not_found=False)
    #     amount=res.price_total
    #     res.update({
    #         'date': fields.Date.context_today(self),
    #         'cost_subtype_id': service and service.id or False,
    #         'cost_type': 'fuel',
    #         'amount':amount
    #     })
    #     return res
    # @api.depends('vendor_id')
    # def _compute_prepaid(self):
    #     for rec in self:
    #         obj_prepaid = self.env['fleet.vehicle.log.fuel.prepaid']
    #         prepaid_id = obj_prepaid.search([
    #             ('operating_unit_id', '=', rec.operating_unit_id.id),
    #             ('vendor_id', '=', rec.vendor_id.id),
    #             ('state', '=', 'confirmed')], limit=1, order="date")
    #         if prepaid_id:
    #             if prepaid_id.balance > rec.price_total:
    #                 rec.prepaid_id = prepaid_id.id
    #             else:
    #                 raise ValidationError(
    #                     _('Insufficient amount'))


    @api.onchange('operating_unit_id')
    def onchange_operating_unit_id(self):
        self.vendor_id = self.operating_unit_id.default_provider_fuel.id

    @api.multi
    @api.depends('vehicle_id')
    def _compute_employee_id(self):
        for rec in self:
            rec.employee_id = rec.travel_id.employee_id

    @api.multi
    @api.depends('tax_amount')
    def _compute_price_subtotal(self):
        for rec in self:
            rec.price_subtotal = rec.price_unit * rec.product_qty
            # if rec.tax_amount > 0:
            #     rec.price_subtotal = rec.tax_amount / 0.16

    @api.multi
    @api.depends('tax_amount')
    def _compute_price_subtotal2(self):
        for rec in self:
            rec.price_subtotal2 = (rec.price_unit * rec.product_qty) - rec.special_tax_amount
            # if rec.tax_amount > 0:
            #     rec.price_subtotal = rec.tax_amount / 0.16

    @api.onchange('tax_amount','product_qty','product_id')
    def _onchange_price_subtotal(self):
        for rec in self:
            rec.price_subtotal = rec.price_unit * rec.product_qty

    @api.multi
    def _compute_price_unit(self):
        for rec in self:
            # rec.price_unit = 0
            # if rec.product_qty and rec.price_subtotal > 0:
            #     rec.price_unit = rec.price_subtotal / rec.product_qty
            rec.price_unit = rec.product_id.standard_price

    @api.multi
    def _compute_taxes(self):
        for rec in self:
            tax = 0
            for t in rec.product_id.supplier_taxes_id:
                tax += t.amount
            rec.tax_amount = rec.product_qty * (rec.product_id.standard_price * (tax/100))

    @api.multi
    def _compute_taxes2(self):
        for rec in self:
            tax = 0
            for t in rec.product_id.supplier_taxes_id:
                tax += t.amount
            rec.tax_amount2 = (rec.price_subtotal2) * (tax/100)

    @api.onchange('product_id','tax_amount','product_qty')
    def _onchange_taxes(self):
        for rec in self:
            tax = 0
            for t in rec.product_id.supplier_taxes_id:
                tax += t.amount
            rec.tax_amount = rec.product_qty * (rec.product_id.standard_price * (tax/100))

    @api.multi
    @api.depends('tax_amount', 'price_subtotal','price_total')
    def _compute_total(self):
        for rec in self:
            rec.price_total = rec.tax_amount + rec.price_subtotal
            # tax = 0
            # for t in rec.product_id.supplier_taxes_id:
            #     tax += t.amount
            # rec.tax_amount = rec.product_qty * (rec.product_id.standard_price * (tax/100))
    @api.multi
    def _compute_total2(self):
        for rec in self:
            rec.price_total2 = rec.tax_amount2 + rec.price_subtotal2
            # tax = 0
            # for t in rec.product_id.supplier_taxes_id:
            #     tax += t.amount
            # rec.tax_amount = rec.product_qty * (rec.product_id.standard_price * (tax/100))

    @api.onchange('price_total','tax_amount','price_subtotal','product_qty')
    def _onchange_total(self):
        for rec in self:
            rec.price_total = rec.tax_amount + rec.price_subtotal


    @api.multi
    @api.depends('price_subtotal', 'tax_amount', 'price_total')
    def _compute_special_tax_amount(self):
        for rec in self:
            rec.special_tax_amount = rec.product_qty * rec.operating_unit_id.ieps_value
            # rec.special_tax_amount = 0
            # if rec.price_subtotal and rec.price_total and rec.tax_amount > 0:
            #     rec.special_tax_amount = (
            #         rec.price_total - rec.price_subtotal - rec.tax_amount)


    permite_exceso = fields.Boolean(string="Permitir Excedente de combustible?", default=False)
    folio_ficha = fields.Char(string="Ficha de deposito")
    adj_ficha = fields.Binary(string="Comprobante")

    @api.multi
    def action_approved(self):
        for rec in self:
            vales = self.env['fleet.vehicle.log.fuel'].search([('travel_id','=',self.travel_id.id),('state','in',['approved','confirmed','closed'])])
            sumva = 0
            for x in vales:
                sumva += x.product_qty
            sumva += self.product_qty
            if sumva > self.travel_id.com_necesario:
                if self.permite_exceso != True:
                    raise ValidationError(
                    _("Al aprovar este vale excede el combustible necesario ("+str(self.travel_id.com_necesario)+" litros), solicite la autorizacion para exceso de combustible."))
                else:
                    rec.message_post(body=_('<b>Fuel Voucher Approved.</b>'))
                    rec.state = 'approved'
            else:
                rec.message_post(body=_('<b>Fuel Voucher Approved.</b>'))
                rec.state = 'approved'
            # rec.message_post(body=_('<b>Fuel Voucher Approved.</b>'))
            # rec.state = 'approved'

    @api.multi
    def action_cancel(self):
        for rec in self:
            if rec.invoice_id:
                raise ValidationError(
                    _('Could not cancel Fuel Voucher! This '
                      'Fuel Voucher is already Invoiced'))
            elif (rec.travel_id and
                  rec.travel_id.state == 'closed'):
                raise ValidationError(
                    _('Could not cancel Fuel Voucher! This Fuel '
                      'Voucher is already linked to a Travel Expense'))
            rec.state = 'cancel'

    @api.model
    def create(self, values):
        res = super(FleetVehicleLogFuel, self).create(values)
        if res:
            ids=res.id
            comb = self.env['fleet.vehicle.log.fuel'].search([('id','=',ids)])
            amount=comb.price_total
            vehicle_id=res.vehicle_id.id
            cost_subtype_id=res.cost_subtype_id.id
            date=res.date
            parent_id=res.parent_id
            do=self.env['fleet.vehicle.cost'].create({'vehicle_id':vehicle_id,'cost_subtype_id':cost_subtype_id,'amount':amount,'date':date,'parent_id':parent_id})
        if not res.operating_unit_id.fuel_log_sequence_id:
            raise ValidationError(_(
                'You need to define the sequence for fuel logs in base %s' %
                res.operating_unit_id.name
            ))
        sequence = res.operating_unit_id.fuel_log_sequence_id
        res.name = sequence.next_by_id()
        return res

    @api.multi
    def set_2_draft(self):
        for rec in self:
            rec.message_post(body=_('<b>Fuel Voucher Draft.</b>'))
            rec.state = 'draft'

    @api.multi
    def action_confirm(self):
        for rec in self:
            if (rec.product_qty <= 0 or
                    rec.tax_amount <= 0 or
                    rec.price_total <= 0):
                raise ValidationError(
                    _('Liters, Taxes and Total'
                      ' must be greater than zero.'))
            rec.message_post(body=_('<b>Fuel Voucher Confirmed.</b>'))
            rec.state = 'confirmed'

    @api.onchange('travel_id')
    def _onchange_travel(self):
        self.vehicle_id = self.travel_id.unit_id
        self.employee_id = self.travel_id.employee_id

    @api.depends('invoice_id')
    def _compute_invoiced_paid(self):
        for rec in self:
            rec.invoice_paid = (
                rec.invoice_id.id and
                rec.invoice_id.state == 'paid')

    @api.multi
    def _amount_to_text(self, product_qty):
        total = str(float(product_qty)).split('.')[0]
        total = num2words(float(total), lang='es').upper()
        return '%s' % (total)

    # @api.model
    # def create(self, vals):
    #     res=super(FleetVehicleLogFuel, self).create(vals)  
      
    #     if res:
    #         ids=res.id
    #         comb = self.env['fleet.vehicle.log.fuel'].search([('id','=',ids)])
    #         amount=comb.price_total
    #         vehicle_id=res.vehicle_id.id
    #         cost_subtype_id=res.cost_subtype_id.id
    #         date=res.date
    #         parent_id=res.parent_id
    #         do=self.env['fleet.vehicle.cost'].create({'vehicle_id':vehicle_id,'cost_subtype_id':cost_subtype_id,'amount':amount,'date':date,'parent_id':parent_id})
                
    #     return res

class FleetVehicleLogFuelTem(models.Model):
    _name = 'fleet.vehicle.log.fuel.tem'
    
    product_qty = fields.Float(string='Liters', default=1.0,)
    vendor_id = fields.Many2one('res.partner')
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        domain=[('tms_product_category', '=', 'fuel')])

    route_id = fields.Many2one('tms.route', string='Ruta')