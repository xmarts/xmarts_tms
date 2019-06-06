# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo import api, fields, models, _


class AttachmentsVehicle(models.Model):
    _name = 'tms.attachment.vehicle'

    name = fields.Char(string='Concepto')
    date = fields.Datetime(string='Fecha')
    adjunto_compro_vehicle = fields.Binary(string="Adjunto")
    filename = fields.Char('file name')


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    _description = "Vehicle"
    _order = 'name'

    attachment_vehicle = fields.One2many('tms.attachment.vehicle', 'name', string="Adjuntos")
    name = fields.Char(compute=False, required=True)
    operating_unit_id = fields.Many2one(
        'operating.unit', string='Operating Unit',default=lambda self: self.env['operating.unit'].search([('name','=','Mexico')], limit=1).id or self.env['operating.unit'].search([('name','=','México')], limit=1).id or '')
    year_model = fields.Char()
    serial_number = fields.Char()
    registration = fields.Char()
    fleet_type = fields.Selection(
        [('tractor', 'Motorized Unit'),
         ('trailer', 'Trailer'),
         ('dolly', 'Dolly'),
         ('other', 'Other')],
        string='Unit Fleet Type')
    notes = fields.Text()
    active = fields.Boolean(default=True)
    driver_id = fields.Many2one('res.partner', string="Driver")
    employee_id = fields.Many2one(
        'hr.employee',
        string="Driver",
        domain=[('driver', '=', True)])
    expense_ids = fields.One2many('tms.expense', 'unit_id', string='Expenses')
    engine_id = fields.Many2one('fleet.vehicle.engine', string='Engine')
    supplier_unit = fields.Boolean()
    unit_extradata = fields.One2many(
        'tms.extradata', 'vehicle_id',
        string='Extra Data Fields',
        readonly=False)
    insurance_policy = fields.Char()
    insurance_policy_data = fields.Char()
    insurance_expiration = fields.Date()
    insurance_supplier_id = fields.Many2one(
        'res.partner', string='Insurance Supplier')
    insurance_days_to_expire = fields.Integer(
        compute='_compute_insurance_days_to_expire', string='Days to expire')

    ejes = fields.Integer(string="Numero de ejes", default=2)
    efficiency = fields.Float(
        digits=(4, 2),
        help=_("Rendimiento L/KM"),
        string=_("Rendimiento L/Km")
    )
    f_category = fields.Many2one("fleet.vehicle.category", string="Categoria")
    f_status = fields.Many2one("fleet.vehicle.state", string="Estado")
    f_status_r = fields.Many2one("fleet.vehicle.status_reason", string="Razon de estado")
    f_marca = fields.Many2one("fleet.vehicle.model.brand", string="Marca")
    #f_tipo_motor = fields.Many2one("fleet.vehicle.motor", string="Tipo de motor")
    @api.depends('insurance_expiration')
    def _compute_insurance_days_to_expire(self):
        for rec in self:
            now = datetime.now()
            date_expire = datetime.strptime(
                rec.insurance_expiration,
                '%Y-%m-%d') if rec.insurance_expiration else datetime.now()
            delta = date_expire - now
            if delta.days >= -1:
                rec.insurance_days_to_expire = delta.days + 1
            else:
                rec.insurance_days_to_expire = 0
