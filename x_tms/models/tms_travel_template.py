# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from __future__ import division
from datetime import datetime, timedelta
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
import random
import mygeotab

# username = 'javier.ramirez@sli.mx'
# password = 'Javier0318*'
# database = 'GSYEECA'

# geo = mygeotab.API(
#         username=username,
#         password=password,
#         database=database
#     )

# authenticate = geo.authenticate()

class TmsTravelTemplate(models.Model):
    _name = 'tms.travel.template'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Plantilla de viaje'

    name = fields.Char('Travel Number')
    route_id = fields.Many2one(
        'tms.route', 'Route', required=True)
    route2_id = fields.Many2one(
        'tms.route', '2da Ruta')
    travel_duration = fields.Float(
        compute='_compute_travel_duration',
        string='Duration Sched',
        help='Travel Scheduled duration in hours')
    distance_route = fields.Float(
        related="route_id.distance",
        string='Route Distance (mi./km)')
    fuel_efficiency_expected = fields.Float(
        compute="")
    kit_id = fields.Many2one(
        'tms.unit.kit', 'Kit')
    unit_id = fields.Many2one(
        'fleet.vehicle', 'Unit',
        required=True)
    trailer1_id = fields.Many2one(
        'fleet.vehicle', 'Remolque 1')
    dolly_id = fields.Many2one(
        'fleet.vehicle', 'Dolly',
        domain=[('fleet_type', '=', 'dolly')])
    trailer2_id = fields.Many2one(
        'fleet.vehicle', 'Remolque 2',
        domain=[('fleet_type', '=', 'trailer')])
    employee_id = fields.Many2one(
        'hr.employee', 'Driver', readonly=True,
        domain=[('driver', '=', True)], related="unit_id.employee_id")
    distance_driver = fields.Float(
        'Distance traveled by driver (mi./km)',
        compute='_compute_distance_driver',
        store=True)
    distance_loaded = fields.Float(
        'Distance Loaded (mi./km)')
    distance_empty = fields.Float(
        'Distance Empty (mi./km)')
    odometer = fields.Float(
        'Unit Odometer (mi./km)', readonly=True)
    fuel_efficiency_travel = fields.Float()
    fuel_efficiency_extraction = fields.Float(
        compute='')
    departure_id = fields.Many2one(
        'tms.place',
        string='Departure',
        compute='_compute_departure_id',
        store=True,
        readonly=True)
    departure2_id = fields.Many2one(
        'tms.place',
        string='2do Origen',
        compute='_compute_departure2_id',
        store=True,
        readonly=True)
    arrival_id = fields.Many2one(
        'tms.place',
        string='Arrival',
        compute='_compute_arrival_id',
        store=True,
        readonly=True)
    arrival2_id = fields.Many2one(
        'tms.place',
        string='2do Destino',
        compute='_compute_arrival2_id',
        store=True,
        readonly=True)
    notes = fields.Text(
        'Description')
    user_id = fields.Many2one(
        'res.users', 'Responsable',
        default=lambda self: self.env.user)
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit')
    color = fields.Integer()
    framework = fields.Selection([
        ('unit', 'Unit'),
        ('single', 'Single'),
        ('double', 'Double')],
        compute='_compute_framework')



    #Agregando campos

    fecha_viaje = fields.Date(string='Fecha del viaje', readonly=False, index=True, copy=False,
                              default=fields.Datetime.now, required=True)

    producto = fields.Many2one("product.template", string="Producto a transportar",required=True)
    costo_producto = fields.Float(string='Costo del producto', track_visibility='onchange')
    sucursal_id = fields.Many2one('tms.sucursal', string='Sucursal', required=True, track_visibility='onchange')
    cliente_id = fields.Many2one('res.partner', string="Cliente", required=True, track_visibility='onchange')
    tarifa_cliente = fields.Float(string='Tarifa cliente', default=0,required=True)
    celular_operador = fields.Char(string='Celular operador', readonly=True, related="employee_id.mobile_phone")
    tipo_viaje = fields.Selection([('Normal', 'Normal'), ('Directo', 'Directo'), ('Cobro destino', 'Cobro destino')],
                                  string='Tipo de viaje', default='Normal', required=True)
    tipo_remolque = fields.Selection([('sencillo','Sencillo'),('doble','Doble')], string="Tipo de remolque", required=True)
    lineanegocio = fields.Many2one(comodel_name='tms.lineanegocio', string='Linea de negocios', store=True)
    tipo_negocio = fields.Selection([('flete','Flete'),('granel','Granel')], string="Tipo", related='lineanegocio.tipo', required=True)
    tipo_lineanegocio = fields.Char('Tipo de linea de negocio', related='lineanegocio.name', store=True)

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.celular_operador = self.employee_id.mobile_phone


    @api.depends('route_id')
    def _compute_departure_id(self):
        for rec in self:
            rec.departure_id = rec.route_id.departure_id

    @api.depends('route_id')
    def _compute_arrival_id(self):
        for rec in self:
            rec.arrival_id = rec.route_id.arrival_id

    @api.depends('route2_id')
    def _compute_departure2_id(self):
        for rec in self:
            rec.departure2_id = rec.route2_id.departure_id

    @api.depends('route2_id')
    def _compute_arrival2_id(self):
        for rec in self:
            rec.arrival2_id = rec.route2_id.arrival_id

    @api.onchange('kit_id')
    def _onchange_kit(self):
        self.unit_id = self.kit_id.unit_id.id
        self.trailer2_id = self.kit_id.trailer2_id.id
        self.trailer1_id = self.kit_id.trailer1_id.id
        self.dolly_id = self.kit_id.dolly_id.id

    @api.onchange('route_id')
    def _onchange_route(self):
        self.travel_duration = self.route_id.travel_time
        self.distance_route = self.route_id.distance
        self.distance_loaded = self.route_id.distance_loaded
        self.distance_empty = self.route_id.distance_empty

    @api.depends('distance_empty', 'distance_loaded')
    def _compute_distance_driver(self):
        for rec in self:
            rec.distance_driver = rec.distance_empty + rec.distance_loaded


    @api.depends('trailer1_id', 'trailer2_id')
    def _compute_framework(self):
        for rec in self:
            if rec.trailer2_id:
                rec.framework = 'double'
            elif rec.trailer1_id:
                rec.framework = 'single'
            else:
                rec.framework = 'unit'

    cargo_id = fields.One2many('tms.viaje.cargos', 'line_cargo_id', string="Cargos Adicionales")


    observaciones = fields.Text(string="Observaciones")
    especificaciones = fields.Text(string="Especificaciones")
    folio_cliente = fields.Char(string="Folio del cliente")

    ejes = fields.Integer(string="Total de ejes.", compute="_total_ejes")
    costo_casetas = fields.Float(string="Costo Total de Casetas", compute="_costo_casetas")

    @api.one
    def _total_ejes(self):
        if self.tipo_remolque == 'doble':
            self.ejes = self.unit_id.ejes + self.trailer1_id.ejes + self.dolly_id.ejes + self.trailer2_id.ejes
        else:
            self.ejes = self.unit_id.ejes + self.trailer1_id.ejes

    @api.one
    def _costo_casetas(self):
        suma = 0
        for x in self.route_id.tollstation_ids:
            for z in x.cost_per_axis_ids:
                if z.axis == self.ejes:
                    suma += z.cost_cash
        for x in self.route2_id.tollstation_ids:
            for z in x.cost_per_axis_ids:
                if z.axis == self.ejes:
                    suma += z.cost_cash
        self.costo_casetas = suma

    kml = fields.Float(string="KM/L", compute="_comp_fuel_kml")
    com_necesario = fields.Float(string="Combustible necesario", compute="_com_com_necesario")
    viaje_gm = fields.Char(string="Viaje GM")
    ruta_vacia1 = fields.Boolean(string="Ruta 1 sin carga?")
    ruta_vacia2 = fields.Boolean(string="Ruta 2 sin carga?")
    rendimiento_manual1= fields.Boolean(string="Rendimiento Manual Ruta 1?")
    rendimiento_manual2= fields.Boolean(string="Rendimiento Manual Ruta 2?")
    kmlmuno = fields.Float(string="KM/L")
    kmlm2 = fields.Float(string="KM/L")
    presupuesto_creado= fields.Boolean(string="Presupuesto creado?", default=False, compute="_com_pres_creado")
