# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from __future__ import division
from datetime import datetime, timedelta
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
import random


class tms_sucursal(models.Model):
    _name = 'tms.sucursal'

    name = fields.Char(string='Nombre',required=True)
    active = fields.Boolean(string="Activo",default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'El nombre no se puede repetir.'),
    ]


class tms_lineanegocio(models.Model):
    _name = 'tms.lineanegocio'

    name = fields.Char(string="Nombre", required=True)
    porcentaje = fields.Float(string="Porcentaje de comisión", required=True)
    tipo = fields.Selection([('flete','Flete'),('granel','Granel')], string="Tipo", required=True)

class TmsTravel(models.Model):
    _name = 'tms.travel'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Travel'
    _order = "date desc"

    waybill_ids = fields.Many2many(
        'tms.waybill', string='Waybills')
    driver_factor_ids = fields.One2many(
        'tms.factor', 'travel_id', string='Travel Driver Payment Factors',
        domain=[('category', '=', 'driver')])
    name = fields.Char('Travel Number')
    state = fields.Selection([
        ('draft', 'Pending'), ('progress', 'In Progress'), ('done', 'Done'),
        ('cancel', 'Cancelled'), ('closed', 'Closed')],
        readonly=True, default='draft')
    route_id = fields.Many2one(
        'tms.route', 'Route', required=True,
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    travel_duration = fields.Float(
        compute='_compute_travel_duration',
        string='Duration Sched',
        help='Travel Scheduled duration in hours')
    travel_duration_real = fields.Float(
        compute='_compute_travel_duration_real',
        string='Duration Real', help="Travel Real duration in hours")
    distance_route = fields.Float(
        related="route_id.distance",
        string='Route Distance (mi./km)')
    fuel_efficiency_expected = fields.Float(
        compute="_compute_fuel_efficiency_expected")
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
        'hr.employee', 'Driver', required=True,
        domain=[('driver', '=', True)])
    date = fields.Datetime(
        'Date  registered', required=True,
        default=(fields.Datetime.now))
    date_start = fields.Datetime(
        'Start Sched',
        default=(fields.Datetime.now))
    date_end = fields.Datetime(
        'End Sched',
        store=True,
        compute='_compute_date_end')
    date_start_real = fields.Datetime(
        'Start Real')
    date_end_real = fields.Datetime(
        'End Real')
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
        compute='_compute_fuel_efficiency_extraction')
    departure_id = fields.Many2one(
        'tms.place',
        string='Departure',
        compute='_compute_departure_id',
        store=True,
        readonly=True)
    fuel_log_ids = fields.One2many(
        'fleet.vehicle.log.fuel', 'travel_id', string='Fuel Vouchers')
    advance_ids = fields.One2many(
        'tms.advance', 'travel_id', string='Advances')
    arrival_id = fields.Many2one(
        'tms.place',
        string='Arrival',
        compute='_compute_arrival_id',
        store=True,
        readonly=True)
    notes = fields.Text(
        'Description')
    user_id = fields.Many2one(
        'res.users', 'Responsable',
        default=lambda self: self.env.user)
    expense_id = fields.Many2one(
        'tms.expense', 'Expense Record', readonly=True)
    event_ids = fields.One2many('tms.event', 'travel_id', string='Events')
    is_available = fields.Boolean(
        compute='_compute_is_available',
        string='Travel available')
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit')
    color = fields.Integer()
    framework = fields.Selection([
        ('unit', 'Unit'),
        ('single', 'Single'),
        ('double', 'Double')],
        compute='_compute_framework')
    partner_ids = fields.Many2many(
        'res.partner', string='Customer', compute='_compute_partner_ids',
        store=True)



    #Agregando campos

    fecha_viaje = fields.Date(string='Fecha del viaje', readonly=False, index=True, copy=False,
                              default=fields.Datetime.now, required=True)
    subpedido_id = fields.Many2one('sale.order', string='Cotización',
                                   required=True, change_default=True, index=True, track_visibility='always')
    product = fields.One2many('sale.order.line', string='Producto', related="subpedido_id.order_line")

    producto = fields.Many2one("product.template", string="Producto a transportar",required=True)
    costo_producto = fields.Float(string='Costo del producto', track_visibility='onchange')
    sucursal_id = fields.Many2one('tms.sucursal', string='Sucursal', required=True, track_visibility='onchange')
    cliente_id = fields.Many2one('res.partner', string="Cliente", required=True, track_visibility='onchange')
    #asociado_id = fields.Many2one('res.partner', string="Asociado", required=True, track_visibility='onchange')

    #porcentaje_comision = fields.Float(string='Porcentaje de comisión', readonly=True)
    #usar_porcentaje = fields.Boolean(string='Usar porcentaje de línea de negocio', readonly=True)
    #tarifa_asociado = fields.Float(string='Tarifa asociado', default=0, track_visibility='onchange', required=True)
    tarifa_cliente = fields.Float(string='Tarifa cliente', default=0,required=True)

    #celular_asociado = fields.Char(string='Celular asociado', required=True)
    celular_operador = fields.Char(string='Celular operador')
    tipo_viaje = fields.Selection([('Normal', 'Normal'), ('Directo', 'Directo'), ('Cobro destino', 'Cobro destino')],
                                  string='Tipo de viaje', default='Normal', required=True)
    tipo_remolque = fields.Selection([('sencillo','Sencillo'),('doble','Doble')], string="Tipo de remolque", required=True)
    lineanegocio = fields.Many2one(comodel_name='tms.lineanegocio', string='Linea de negocios', store=True)
    tipo_lineanegocio = fields.Char('Tipo de linea de negocio', related='lineanegocio.name', store=True)
    flete_cliente = fields.Float(string='Flete cliente', readonly=True, compute='_compute_flete_cliente')

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.celular_operador = self.employee_id.mobile_phone

    @api.onchange('subpedido_id')
    def onchange_subpedido_id(self):
        self.tarifa_cliente = self.subpedido_id.tarifa_cliente
        self.route_id = self.subpedido_id.ruta
        self.producto = self.subpedido_id.product
        self.costo_producto = self.subpedido_id.product.standard_price
        self.cliente_id = self.subpedido_id.partner_id

    @api.constrains('lineanegocio', 'sucursal_id',
                    'peso_origen_remolque_1', 'peso_origen_remolque_2', 'peso_destino_remolque_1',
                    'peso_destino_remolque_2', 'peso_convenido_remolque_1', 'peso_convenido_remolque_2')
    def _valida(self):
        # if not self.cliente_id:
        #     raise UserError(_('Alerta !\n--Debe especificar el cliente.'))

        if not self.lineanegocio:
            raise UserError(_('Alerta !\nDebe especificar la línea de negocio.'))

        # if not self.asociado_id:
        #     raise UserError(_('Alerta !\nDebe especificar el asociado.'))

        if not self.sucursal_id:
            raise UserError(_('Alerta !\nDebe especificar la sucursal.'))

        # if not self.placas_id:
        #     raise UserError(_('Alerta !\nDebe especificar el vehículo.'))

        # if not self.asociado_id:
        #     raise UserError(_('Alerta !\nDebe especificar el asociado.'))

        # total_viajes = self.total_viajes()
        # total_subpedido = self.subpedido_id.cantidad

        # print("================Total viajes:: " + str(total_viajes) + " Total subpedido:: " + str(total_subpedido))
        # if total_viajes > 0 and total_subpedido > 0 and total_viajes > total_subpedido:
        #     raise UserError(_(
        #         'Alerta..\nCon el viaje actual se excede el peso de lo especificado en la cotización ({}/{}).'.format(
        #             total_viajes, total_subpedido)))

        # Pesos
        if self.lineanegocio.id == 1:  # Si es granel.
            if self.peso_origen_remolque_1 > 0 and (self.peso_origen_remolque_1 > 70000):
                raise UserError(_('Alerta !\nEl peso origen del remolque 1 debe estar entre 1 y 70,000.'))

            if self.peso_origen_remolque_2 > 0 and (self.peso_origen_remolque_2 > 70000):
                raise UserError(_('Alerta !\nEl peso origen del remolque 2 debe estar entre 1 y 70,000.'))

            if self.peso_destino_remolque_1 > 0 and (self.peso_destino_remolque_1 > 70000):
                raise UserError(_('Alerta !\nEl peso destino del remolque 1 debe estar entre 1 y 70,000.'))

            if self.peso_destino_remolque_2 > 0 and (self.peso_destino_remolque_2 > 70000):
                raise UserError(_('Alerta !\nEl peso destino del remolque 2 debe estar entre 1 y 70,000.'))

            if self.peso_convenido_remolque_1 > 0 and (self.peso_convenido_remolque_1 > 70000):
                raise UserError(_('Alerta !\nEl peso convenido del remolque 1 debe estar entre 1 y 70,000.'))

            if self.peso_convenido_remolque_2 > 0 and (self.peso_convenido_remolque_2 > 70000):
                raise UserError(_('Alerta !\nEl peso convenido del remolque 2 debe estar entre 1 y 70,000.'))

    # @api.onchange('lineanegocio')
    # def _onchange_lineanegocio(self):
    #     if self.lineanegocio:
    #         if self.lineanegocio.id == 3:
    #             # if self.tipo_remolque.tipo == 'sencillo':
    #             #     self.peso_origen_remolque_1 = 1000
    #             #     self.peso_origen_remolque_2 = 0
    #             #     self.peso_destino_remolque_1 = 1000
    #             #     self.peso_destino_remolque_2 = 0
    #             # else:
    #             #     self.peso_origen_remolque_1 = 500
    #             #     self.peso_origen_remolque_2 = 500
    #             #     self.peso_destino_remolque_1 = 500
    #             #     self.peso_destino_remolque_2 = 500
    #             self.peso_origen_remolque_1 = 500
    #             self.peso_origen_remolque_2 = 500
    #             self.peso_destino_remolque_1 = 500
    #             self.peso_destino_remolque_2 = 500
    #         else:
    #             self.peso_origen_remolque_1 = 0
    #             self.peso_origen_remolque_2 = 0
    #             self.peso_destino_remolque_1 = 0
    #             self.peso_destino_remolque_2 = 0

    peso_origen_remolque_1 = fields.Float(string='Peso remolque 1 Kg', track_visibility='onchange')
    peso_origen_remolque_2 = fields.Float(string='Peso remolque 2 Kg', track_visibility='onchange')
    peso_destino_remolque_1 = fields.Float(string='Peso remolque 1 Kg', track_visibility='onchange')
    peso_destino_remolque_2 = fields.Float(string='Peso remolque 2 Kg', track_visibility='onchange')
    peso_convenido_remolque_1 = fields.Float(string='Peso remolque 1 Kg', track_visibility='onchange')
    peso_convenido_remolque_2 = fields.Float(string='Peso remolque 2 Kg', track_visibility='onchange')
    peso_autorizado = fields.Float(string='Peso autorizado Tons', track_visibility='onchange')

    @api.one
    @api.depends('peso_origen_remolque_1','peso_origen_remolque_2')
    def _compute_pesos_origen_total(self):
            self.peso_origen_total = self.peso_origen_remolque_1 + self.peso_origen_remolque_2

    @api.one
    @api.depends('lineanegocio','peso_origen_total','tarifa_cliente','facturar_con_cliente','peso_convenido_total','peso_origen_total','peso_destino_total')
    def _compute_flete_cliente(self):
        for reg in self:
            if self.lineanegocio.tipo == 'granel':
                if reg.facturar_con_cliente == 'Peso convenido':
                    reg.flete_cliente = (reg.peso_convenido_total / 1000) * reg.tarifa_cliente
                elif reg.facturar_con_cliente == 'Peso origen':
                    reg.flete_cliente = (reg.peso_origen_total / 1000) * reg.tarifa_cliente
                elif reg.facturar_con_cliente == 'Peso destino':
                    reg.flete_cliente = (reg.peso_destino_total / 1000) * reg.tarifa_cliente
            if self.lineanegocio.tipo == 'flete':
                reg.flete_cliente = reg.tarifa_cliente

    @api.one
    @api.depends('peso_destino_remolque_1','peso_destino_remolque_2')
    def _compute_pesos_destino_total(self):
            self.peso_destino_total = self.peso_destino_remolque_1 + self.peso_destino_remolque_2

    @api.one
    @api.depends('peso_convenido_remolque_1','peso_convenido_remolque_2')
    def _compute_pesos_convenido_total(self):
            self.peso_convenido_total = self.peso_convenido_remolque_1 + self.peso_convenido_remolque_2


    peso_origen_total = fields.Float(string='Peso total Kg', compute='_compute_pesos_origen_total')
    peso_destino_total = fields.Float(string='Peso total Kg', compute='_compute_pesos_destino_total')
    peso_convenido_total = fields.Float(string='Peso total Kg', compute='_compute_pesos_convenido_total')


    facturar_con = fields.Selection(
        [('Peso convenido', 'Peso convenido'), ('Peso origen', 'Peso origen'), ('Peso destino', 'Peso destino')],
        string='Facturar con (Asociado)', required=True, default='Peso origen', track_visibility='onchange')

    facturar_con_cliente = fields.Selection(
        [('Peso convenido', 'Peso convenido'), ('Peso origen', 'Peso origen'), ('Peso destino', 'Peso destino')],
        string='Facturar con (Cliente)', required=True, default='Peso origen', track_visibility='onchange')
    excedente_merma = fields.Selection(
        [('No cobrar', 'No cobrar'), ('Porcentaje: Cobrar diferencia', 'Porcentaje: Cobrar diferencia'),
         ('Porcentaje: Cobrar todo', 'Porcentaje: Cobrar todo'), ('Kg: Cobrar diferencia', 'Kg: Cobrar diferencia'),
         ('Kg: Cobrar todo', 'Kg: Cobrar todo'), ('Cobrar todo', 'Cobrar todo')],
        string='Si la merma excede lo permitido', required=True, default='Porcentaje: Cobrar diferencia')


    @api.onchange('peso_origen_total', 'peso_destino_total')
    def _onchange_merma_kg_(self):
        self.merma_kg = 0
        if self.peso_origen_total and self.peso_destino_total:
            if self.peso_destino_total > self.peso_origen_total:
                self.merma_kg = 0
            else:
                self.merma_kg = self.peso_origen_total - self.peso_destino_total
        else:
            self.merma_kg = 0

    @api.one
    def _compute_merma_kg_(self):
        self.merma_kg = 0
        if self.peso_origen_total and self.peso_destino_total:
            if self.peso_destino_total > self.peso_origen_total:
                self.merma_kg = 0
            else:
                self.merma_kg = self.peso_origen_total - self.peso_destino_total
        else:
            self.merma_kg = 0

    merma_kg = fields.Float(string='Merma Kg', readonly=True,compute="_compute_merma_kg_")

    @api.onchange('peso_origen_total', 'peso_destino_total', 'tipo_remolque')
    def _onchange_merma_pesos(self):
        if self.peso_origen_total and self.peso_destino_total:
            # if 'Contenedor' in self.tipo_remolque.name:
            if self.lineanegocio.tipo == 'flete':  # Contenedores.
                self.merma_pesos = 0
            else:
                self.merma_pesos = self.merma_kg * self.costo_producto
        else:
            self.merma_pesos = 0

    @api.depends('merma_kg')
    @api.one
    def _compute_merma_pesos(self):
        if self.peso_origen_total and self.peso_destino_total:
            if self.lineanegocio.tipo == 'flete':  # Contenedores.
                self.merma_pesos = 0
            else:
                self.merma_pesos = self.merma_kg * self.costo_producto
        else:
            self.merma_pesos = 0

    merma_pesos = fields.Float(string='Merma $', readonly=True, compute="_compute_merma_pesos")

    @api.onchange('excedente_merma', 'peso_origen_total', 'peso_destino_total')
    def _onchange_merma_permitida_kg(self):
        if self.peso_origen_total and self.peso_destino_total:
            if self.excedente_merma:
                if self.excedente_merma == 'No cobrar':
                    self.merma_permitida_kg = 0
                else:
                    if self.cliente_id.merma_permitida_por:
                        if self.peso_origen_total > self.peso_destino_total:
                            self.merma_permitida_kg = self.cliente_id.merma_permitida_por * (self.peso_origen_total / 100)
                        else:
                            self.merma_permitida_kg = 0
        else:
            self.merma_permitida_kg = 0

    # @api.onchange('peso_origen_remolque_1', 'peso_origen_remolque_2', 'peso_destino_remolque_1',
    #               'peso_destino_remolque_2')
    # def _calcula_cargosx(self):
    #     pesoo_r1 = 0
    #     pesoo_r2 = 0
    #     pesod_r1 = 0
    #     pesod_r2 = 0
    #     pesoo = 0
    #     pesod = 0

    #     merma_kg = 0
    #     merma_m = 0

    #     merma_c_kg = 0
    #     merma_c_m = 0

    #     if self.peso_origen_remolque_1:
    #         pesoo_r1 = self.peso_origen_remolque_1

    #     if self.peso_origen_remolque_2:
    #         pesoo_r2 = self.peso_origen_remolque_2

    #     if self.peso_destino_remolque_1:
    #         pesod_r1 = self.peso_destino_remolque_1

    #     if self.peso_destino_remolque_2:
    #         pesod_r2 = self.peso_destino_remolque_2

    #     if pesoo_r1 > 0 and pesod_r1 > 0 and pesoo_r1 > pesod_r1:
    #         merma_kg += pesoo_r1 - pesod_r1

    #     if pesoo_r2 > 0 and pesod_r2 > 0 and pesoo_r2 > pesod_r2:
    #         merma_kg += pesoo_r2 - pesod_r2

    #     pesoo = pesoo_r1 + pesoo_r2
    #     pesod = pesod_r1 + pesod_r2

    #     print("**********MERMA KG: " + str(merma_kg))

    @api.one
    def _compute_merma_permitida_kg(self):
        if self.peso_origen_total and self.peso_destino_total:
            if self.excedente_merma:
                if self.excedente_merma == 'No cobrar':
                    self.merma_permitida_kg = 0
                else:
                    if self.cliente_id.merma_permitida_por:
                        if self.peso_origen_total > self.peso_destino_total:
                            self.merma_permitida_kg = self.cliente_id.merma_permitida_por * (
                            self.peso_origen_total / 100)
                        else:
                            self.merma_permitida_kg = 0
        else:
            self.merma_permitida_kg = 0

    merma_permitida_kg = fields.Float(string='Merma permitida Kg', readonly=True, compute="_compute_merma_permitida_kg")

    @api.onchange('merma_permitida_kg', 'costo_producto')
    def _onchange_merma_permitida_pesos(self):
        if self.peso_origen_total and self.peso_destino_total:
            if self.merma_permitida_kg:
                self.merma_permitida_pesos = self.merma_permitida_kg * self.costo_producto
            else:
                self.merma_permitida_pesos = 0
        else:
            self.merma_permitida_pesos = 0

    @api.one
    def _compute_merma_permitida_pesos(self):
        if self.peso_origen_total and self.peso_destino_total:
            if self.merma_permitida_kg:
                self.merma_permitida_pesos = self.merma_permitida_kg * self.costo_producto
            else:
                self.merma_permitida_pesos = 0
        else:
            self.merma_permitida_pesos = 0

    merma_permitida_pesos = fields.Float(string='Merma permitida $',readonly=True,compute="_compute_merma_permitida_pesos")

    @api.onchange('peso_origen_remolque_1', 'peso_origen_remolque_2', 'peso_destino_remolque_1',
                  'peso_destino_remolque_2')
    def _onchange_merma_total(self):
        if self.peso_origen_remolque_1 > self.peso_destino_remolque_1:
            merma_origen = self.peso_origen_remolque_1 - self.peso_destino_remolque_1
        else:
            merma_origen = 0
        if self.peso_origen_remolque_2 > self.peso_destino_remolque_2:
            merma_destino = self.peso_origen_remolque_2 - self.peso_destino_remolque_2
        else:
            merma_destino = 0
        self.merma_total = merma_origen + merma_destino

    @api.one
    def _compute_merma_total(self):
        if self.peso_origen_remolque_1 > self.peso_destino_remolque_1:
            merma_origen = self.peso_origen_remolque_1 - self.peso_destino_remolque_1
        else:
            merma_origen = 0
        if self.peso_origen_remolque_2 > self.peso_destino_remolque_2:
            merma_destino = self.peso_origen_remolque_2 - self.peso_destino_remolque_2
        else:
            merma_destino = 0
        self.merma_total = merma_origen + merma_destino

    merma_total = fields.Float(string='Merma total kg', readonly=True, compute="_compute_merma_total")

    @api.onchange('merma_kg', 'merma_permitida_kg')
    def _onchange_diferencia_porcentaje(self):
        if self.merma_kg > self.merma_permitida_kg:
            self.diferencia_porcentaje = self.merma_kg - self.merma_permitida_kg
        else:
            self.diferencia_porcentaje = 0

    @api.one
    def _compute_diferencia_porcentaje(self):
        if self.merma_kg > self.merma_permitida_kg:
            self.diferencia_porcentaje = self.merma_kg - self.merma_permitida_kg
        else:
            self.diferencia_porcentaje = 0

    diferencia_porcentaje = fields.Float(string='diferencia_porcentaje kg',
                                         readonly=True)

    diferencia_kg = fields.Float(string='diferencia_porcentaje kg', compute='_compute_diferencia_kg',
                                 readonly=True)

    @api.onchange('excedente_merma', 'merma_permitida_kg', 'diferencia_porcentaje', 'diferencia_kg',
                  'peso_origen_total', 'peso_destino_total')
    def _onchange_merma_cobrar_kg(self):
        if self.peso_origen_total > self.peso_destino_total:
            if self.excedente_merma:
                if self.excedente_merma == 'No cobrar':
                    self.merma_cobrar_kg = 0
                if self.excedente_merma == 'Porcentaje: Cobrar diferencia':
                    if self.merma_kg > self.merma_permitida_kg:
                        self.merma_cobrar_kg = self.merma_kg - self.merma_permitida_kg
                    else:
                        self.merma_cobrar_kg = 0
                if self.excedente_merma == 'Porcentaje: Cobrar todo':
                    if self.merma_kg > self.merma_permitida_kg:
                        self.merma_cobrar_kg = self.merma_kg
                    else:
                        self.merma_cobrar_kg = 0
                if self.excedente_merma == 'Kg: Cobrar diferencia':
                    if self.merma_kg > self.cliente_id.merma_permitida_kg:
                        self.merma_cobrar_kg = self.merma_kg - self.cliente_id.merma_permitida_kg
                    else:
                        self.merma_cobrar_kg = 0
                if self.excedente_merma == 'Kg: Cobrar todo':
                    if self.merma_kg > self.cliente_id.merma_permitida_kg:
                        self.merma_cobrar_kg = self.merma_kg
                    else:
                        self.merma_cobrar_kg = 0
                if self.excedente_merma == 'Cobrar todo':
                    self.merma_cobrar_kg = self.merma_kg
        else:
            self.merma_cobrar_kg = 0

    @api.one
    @api.depends('peso_origen_total', 'peso_destino_total', 'merma_kg', 'merma_permitida_kg', 'diferencia_porcentaje',
                 'diferencia_kg')
    def _compute_merma_cobrar_kg(self):
        if self.peso_origen_total > self.peso_destino_total:
            if self.excedente_merma:
                if self.excedente_merma == 'No cobrar':
                    self.merma_cobrar_kg = 0
                if self.excedente_merma == 'Porcentaje: Cobrar diferencia':
                    if self.merma_kg > self.merma_permitida_kg:
                        self.merma_cobrar_kg = self.merma_kg - self.merma_permitida_kg
                    else:
                        self.merma_cobrar_kg = 0
                if self.excedente_merma == 'Porcentaje: Cobrar todo':
                    if self.merma_kg > self.merma_permitida_kg:
                        self.merma_cobrar_kg = self.merma_kg
                    else:
                        self.merma_cobrar_kg = 0
                if self.excedente_merma == 'Kg: Cobrar diferencia':
                    if self.merma_kg > self.cliente_id.merma_permitida_kg:
                        self.merma_cobrar_kg = self.merma_kg - self.cliente_id.merma_permitida_kg
                    else:
                        self.merma_cobrar_kg = 0
                if self.excedente_merma == 'Kg: Cobrar todo':
                    if self.merma_kg > self.cliente_id.merma_permitida_kg:
                        self.merma_cobrar_kg = self.merma_kg
                    else:
                        self.merma_cobrar_kg = 0
                if self.excedente_merma == 'Cobrar todo':
                    self.merma_cobrar_kg = self.merma_kg
        else:
            self.merma_cobrar_kg = 0

    merma_cobrar_kg = fields.Float(string='Merma cobrar kg', readonly=True, compute="_compute_merma_cobrar_kg")

    @api.onchange('merma_cobrar_kg', 'costo_producto')
    def _onchange_merma_cobrar_pesos(self):
        if self.merma_cobrar_kg > 0:
            self.merma_cobrar_pesos = self.merma_cobrar_kg * self.costo_producto
        else:
            self.merma_cobrar_pesos = 0

    @api.one
    @api.depends('merma_cobrar_kg', 'costo_producto')
    def _compute_merma_cobrar_pesos(self):
        if self.merma_cobrar_kg > 0:
            self.merma_cobrar_pesos = self.merma_cobrar_kg * self.costo_producto
            # self.merma_cobrar_pesos = merma_cobrar_pesos
            # valores = {'viaje_id': self.id, 'monto': self.merma_cobrar_pesos, 'tipo_cargo': 'merma',
            #            'asociado_id': self.asociado_id.id}
            # obc_cargos = self.env['trafitec.cargos'].search(
            #     ['&', ('viaje_id', '=', self.id), ('tipo_cargo', '=', 'merma')])
            # if len(obc_cargos) == 0:
            #     self.env['trafitec.cargos'].create(valores)
            # else:
            #     obc_cargos.write(valores)
        else:
            self.merma_cobrar_pesos = 0

    merma_cobrar_pesos = fields.Float(string='Merma cobrar $', readonly=True, compute="_compute_merma_cobrar_pesos")




    # comision_linea = fields.Float(string='Porcentaje linea negocio', readonly=True, related='lineanegocio.porcentaje')
    # regla_comision = fields.Selection([('No cobrar', 'No cobrar'),
    #                                    ('Con % linea transportista y peso origen',
    #                                     'Con % linea transportista y peso origen'),
    #                                    ('Con % linea transportista y peso destino',
    #                                     'Con % linea transportista y peso destino'),
    #                                    ('Con % linea transportista y peso convenido',
    #                                     'Con % linea transportista y peso convenido'),
    #                                    ('Con % linea transportista y capacidad de remolque',
    #                                     'Con % linea transportista y capacidad de remolque'),
    #                                    ('Con % especifico y peso origen', 'Con % especifico y peso origen'),
    #                                    ('Con % especifico y peso destino', 'Con % especifico y peso destino'),
    #                                    ('Con % especifico y peso convenido', 'Con % especifico y peso convenido'),
    #                                    ('Con % especifico y capacidad de remolque',
    #                                     'Con % especifico y capacidad de remolque'),
    #                                    ('Cobrar cantidad especifica', 'Cobrar cantidad específica')],
    #                                   string='Regla de Comisión', default='Con % linea transportista y peso origen',
    #                                   required=True, track_visibility='onchange')
    # comision = fields.Selection([('No cobrar', 'No cobrar'), ('Cobrar en contra-recibo', 'Cobrar en contra-recibo'), (
    # 'Cobrar en contra recibo-porcentaje especifico', 'Cobrar en contra recibo-porcentaje específico'),
    #                              ('Cobrar cantidad especifica', 'Cobrar cantidad específica')], string='Comisión',
    #                             default='Cobrar en contra-recibo', required=True, track_visibility='onchange')

    # pronto_pago = fields.Boolean(sring='Pronto pago', default=False)

    # comision_calculada = fields.Float(string='Comisión calculada', readonly=True)
    # motivo = fields.Text(string='Motivo sin comisión', track_visibility='onchange')
    # porcent_comision = fields.Float(string='Porcentaje de comisión')
    # cant_especifica = fields.Float(string='Cobrar cantidad específica')
    peso_autorizado = fields.Float(string='Peso autorizado Tons', required=True)
    tipo_viaje = fields.Selection([('Normal', 'Normal'), ('Directo', 'Directo'), ('Cobro destino', 'Cobro destino')],
                                  string='Tipo de viaje', default='Normal', required=True)
    # maniobras = fields.Float(string='Maniobras')
    # regla_maniobra = fields.Selection(
    #     [('Pagar en contrarecibo y cobrar en factura', 'Pagar en contrarecibo y cobrar en factura'),
    #      ('Pagar en contrarecibo y no cobrar en factura', 'Pagar en contrarecibo y no cobrar en factura'),
    #      ('No pagar en contrarecibo y cobrar en factura', 'No pagar en contrarecibo y cobrar en factura'),
    #      ('No pagar en contrarecibo y no cobrar en factura', 'No pagar en contrarecibo y no cobrar en factura')],
    #     string='Regla de maniobra', default='Pagar en contrarecibo y cobrar en factura', required=True,
    #     track_visibility='onchange')

    # @api.constrains('regla_comision', 'motivo', 'porcent_comision', 'cant_especifica')
    # def _check_comision_motivo(self):
    #     if self.regla_comision == 'No cobrar':
    #         if self.motivo == False:
    #             raise UserError(
    #                 _('Aviso !\nDebe capturar el motivo por el cual no se cobra comisión'))
    #     if 'Con % especifico' in self.regla_comision:
    #         if self.porcent_comision == 0 or self.porcent_comision == 0.00:
    #             raise UserError(
    #                 _('Aviso !\nDebe capturar el porcentaje de la comisión'))
    #     if self.regla_comision == 'Cobrar cantidad especifica':
    #         if self.cant_especifica == 0 or self.cant_especifica == 0.00:
    #             raise UserError(
    #                 _('Aviso !\nDebe capturar la cantidad especifica'))


    #Agregando campos


    @api.depends('waybill_ids')
    def _compute_partner_ids(self):
        for rec in self:
            partner_ids = []
            for waybill in rec.waybill_ids:
                partner_ids.append(waybill.partner_id.id)
            rec.partner_ids = partner_ids

    @api.depends('route_id')
    def _compute_departure_id(self):
        for rec in self:
            rec.departure_id = rec.route_id.departure_id

    @api.depends('route_id')
    def _compute_arrival_id(self):
        for rec in self:
            rec.arrival_id = rec.route_id.arrival_id

    @api.depends('fuel_efficiency_expected', 'fuel_efficiency_travel')
    def _compute_fuel_efficiency_extraction(self):
        for rec in self:
            rec.fuel_efficiency_extraction = (
                rec.fuel_efficiency_expected - rec.fuel_efficiency_travel)

    @api.depends('date_start')
    def _compute_date_end(self):
        for rec in self:
            if rec.date_start:
                strp_date = datetime.strptime(
                    rec.date_start, "%Y-%m-%d %H:%M:%S")
                rec.date_end = strp_date + timedelta(
                    hours=rec.route_id.travel_time)

    @api.depends('date_start', 'date_end')
    def _compute_travel_duration(self):
        for rec in self:
            if rec.date_start and rec.date_end:
                start_date = datetime.strptime(
                    rec.date_start, "%Y-%m-%d %H:%M:%S")
                end_date = datetime.strptime(rec.date_end, "%Y-%m-%d %H:%M:%S")
                difference = (end_date - start_date).total_seconds() / 60 / 60
                rec.travel_duration = difference

    @api.depends('date_start_real', 'date_end_real')
    def _compute_travel_duration_real(self):
        for rec in self:
            if rec.date_start_real and rec.date_end_real:
                start_date = datetime.strptime(
                    rec.date_start_real, "%Y-%m-%d %H:%M:%S")
                end_date = datetime.strptime(
                    rec.date_end_real, "%Y-%m-%d %H:%M:%S")
                difference = (end_date - start_date).total_seconds() / 60 / 60
                rec.travel_duration_real = difference

    @api.onchange('kit_id')
    def _onchange_kit(self):
        self.unit_id = self.kit_id.unit_id.id
        self.trailer2_id = self.kit_id.trailer2_id.id
        self.trailer1_id = self.kit_id.trailer1_id.id
        self.dolly_id = self.kit_id.dolly_id.id
        self.employee_id = self.kit_id.employee_id.id

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

    @api.multi
    def action_draft(self):
        for rec in self:
            rec.state = "draft"

    @api.multi
    def action_progress(self):
        for rec in self:
            rec.validate_driver_license()
            rec.validate_vehicle_insurance()
            travels = rec.search(
                [('state', '=', 'progress'), '|',
                 ('employee_id', '=', rec.employee_id.id),
                 ('unit_id', '=', rec.unit_id.id)])
            if len(travels) >= 1:
                raise ValidationError(
                    _('The unit or driver are already in use!'))
            rec.state = "progress"
            rec.date_start_real = fields.Datetime.now()
            rec.message_post('Travel Dispatched')

    @api.multi
    def action_done(self):
        for rec in self:
            odometer = self.env['fleet.vehicle.odometer'].create({
                'travel_id': rec.id,
                'vehicle_id': rec.unit_id.id,
                'last_odometer': rec.unit_id.odometer,
                'distance': rec.distance_driver,
                'current_odometer': rec.unit_id.odometer + rec.distance_driver,
                'value': rec.unit_id.odometer + rec.distance_driver
            })
            rec.state = "done"
            rec.odometer = odometer.current_odometer
            rec.date_end_real = fields.Datetime.now()
            rec.message_post('Travel Finished')

    @api.multi
    def action_cancel(self):
        for rec in self:
            advances = rec.advance_ids.search([
                ('state', '!=', 'cancel'),
                ('travel_id', '=', rec.id)])
            fuel_log = rec.fuel_log_ids.search([
                ('state', '!=', 'cancel'),
                ('travel_id', '=', rec.id)])
            if len(advances) >= 1 or len(fuel_log) >= 1:
                raise ValidationError(
                    _('If you want to cancel this travel,'
                      ' you must cancel the fuel logs or the advances '
                      'attached to this travel'))
            rec.state = "cancel"
            rec.message_post('Travel Cancelled')

    @api.model
    def create(self, values):
        travel = super(TmsTravel, self).create(values)
        if not travel.operating_unit_id.travel_sequence_id:
            raise ValidationError(_(
                'You need to define the sequence for travels in base %s' %
                travel.operating_unit_id.name
            ))
        sequence = travel.operating_unit_id.travel_sequence_id
        travel.name = sequence.next_by_id()
        return travel

    @api.depends()
    def _compute_is_available(self):
        for rec in self:
            objects = ['tms.advance', 'fleet.vehicle.log.fuel', 'tms.waybill']
            advances = len(rec.advance_ids)
            fuel_vehicle = len(rec.fuel_log_ids)
            count = 0
            for model in objects:
                if model == 'tms.advance' or model == 'fleet.vehicle.log.fuel':
                    object_ok = len(rec.env[model].search(
                        [('state', '=', 'confirmed'),
                         ('travel_id', '=', rec.id)]))
                    if (model == 'tms.advance' and
                            advances == object_ok or advances == 0):
                        count += 1
                    elif (model == 'fleet.vehicle.log.fuel' and
                            fuel_vehicle == object_ok or fuel_vehicle == 0):
                        count += 1
                if model == 'tms.waybill':
                    object_ok = len(rec.env[model].search(
                        [('state', '=', 'confirmed'),
                         ('travel_ids', 'in', rec.id)]))
                    if len(rec.waybill_ids) == object_ok:
                        count += 1
            if count == 3:
                rec.is_available = True

    @api.depends('route_id', 'framework')
    def _compute_fuel_efficiency_expected(self):
        for rec in self:
            res = self.env['tms.route.fuelefficiency'].search([
                ('route_id', '=', rec.route_id.id),
                ('engine_id', '=', rec.unit_id.engine_id.id),
                ('type', '=', rec.framework)
            ]).performance
            rec.fuel_efficiency_expected = res

    @api.depends('trailer1_id', 'trailer2_id')
    def _compute_framework(self):
        for rec in self:
            if rec.trailer2_id:
                rec.framework = 'double'
            elif rec.trailer1_id:
                rec.framework = 'single'
            else:
                rec.framework = 'unit'

    @api.multi
    def validate_driver_license(self):
        val = self.env['ir.config_parameter'].get_param(
            'driver_license_security_days')
        days = int(val) or 0
        for rec in self:
            if rec.employee_id.days_to_expire <= days:
                raise ValidationError(
                    _("You can not Dispatch this Travel because %s "
                      "Driver s License Validity %s is expired or"
                      " about to expire in next %s days") % (
                        rec.employee_id.name,
                        rec.employee_id.license_expiration, val))

    @api.multi
    def validate_vehicle_insurance(self):
        val = self.env['ir.config_parameter'].get_param(
            'tms_vehicle_insurance_security_days')
        xdays = int(val) or 0
        date = datetime.now() + timedelta(days=xdays)
        for rec in self:
            units = [
                rec.unit_id, rec.trailer1_id, rec.dolly_id, rec.trailer2_id]
            for unit in units:
                if (unit and unit.insurance_expiration and
                        unit.insurance_expiration <= date.strftime(
                            '%Y-%m-%d')):
                    raise ValidationError(_(
                        "You can not Dispatch this Travel because this Vehicle"
                        " %s Insurance %s is expired or about to expire in "
                        "next %s days") % (
                        rec.unit_id.name, rec.unit_id.insurance_expiration,
                        val))

    @api.multi
    def copy(self, default=None):
        default = dict(default or {})
        default['waybill_ids'] = False
        return super(TmsTravel, self).copy(default)



    evidencias_id = fields.One2many(string="Evidencias",comodel_name="tms.viajes.evidencias", inverse_name="linea_id", track_visibility='onchange')
    documentacion_completa = fields.Boolean(string='Documentanción completa', default=False)
    fecha_documentacion = fields.Date(string="Fecha documentación")
    #dif_dias = fields.Integer(string="Dias", default=0)
    asignadoa_id = fields.Many2one("res.users", string="Asignado a")
    boletas_id = fields.One2many(comodel_name="tms.viajes.boletas", inverse_name="linea_id",track_visibility='onchange', string="Boletas")

    detalle_origen = fields.Text(string="Detalle Origen")
    detalle_destino = fields.Text(string="Detalle Destino")

    fecha_hora_carga = fields.Datetime(string="Fecha y hora de carga")
    fecha_hora_descarga = fields.Datetime(string="Fecha y hora de descarga")
    detalles_cita = fields.Text(string="Detalles de cita")

    cargo_id = fields.One2many('tms.viaje.cargos', 'line_cargo_id', string="Cargos Adicionales")

    calificaiones = fields.One2many(string = 'Calificaciones',inverse_name='viaje_id', comodel_name = 'tms.calificacionesgxviaje', track_visibility='onchange')




    observaciones = fields.Text(string="Observaciones")
    especificaciones = fields.Text(string="Especificaciones")
    folio_cliente = fields.Char(string="Folio del cliente")
    suger_pago = fields.Boolean(string="Sugerir pago inmediato")

    @api.constrains('evidencia_id', 'documentacion_completa', 'name')
    def _check_evidencia(self):
        if self.documentacion_completa == True:
            obj_eviden = self.env['tms.viajes.evidencias'].search(
                ['&', ('linea_id', '=', self.id), ('name', '=', 'Evidencia de viaje')])
            if len(obj_eviden) == 0:
                raise UserError(
                    _('Aviso !\nNo puede aplicar como documentación completa, si no tiene ninguna evidencia de viaje'))



    #--------------------------------------------------------------------------------------------------------------------------------------
    #SLI TRACK
    #--------------------------------------------------------------------------------------------------------------------------------------
    slitrack_gps_latitud = fields.Float(string='Latitud', default=0, digits=(10, 10))
    slitrack_gps_longitud = fields.Float(string='Longitud', default=0, digits=(10, 10))
    slitrack_gps_velocidad = fields.Float(string='Velocidad', default=0)
    slitrack_gps_fechahorar = fields.Datetime(string='Fecha y hora')
    slitrack_comentarios = fields.Text(string='Comentarios', defaut='')
    slitrack_estado = fields.Selection(string='Estado',selection=[('noiniciado', '(No iniciado)'), ('iniciado', 'Iniciado'),('terminado', 'Terminado')], default='noiniciado')
    slitrack_codigo = fields.Char(string='Código', default='')
    slitrack_gps_contador = fields.Integer(string='Contador', default=0)
    slitrack_st = fields.Selection(string='Activo', selection=[('inactivo', 'Inactivo'), ('activo', 'Activo')],default='inactivo')

    slitrack_registro=fields.One2many(string='Registro',comodel_name='tms.slitrack.registro',inverse_name='viaje_id')
    slitrack_proveedor=fields.Selection(string="Tipo",selection=[('slitrack','SLI Track'),('geotab','GeoTab'),('manual','Manual')],default='manual')

    def action_slitrack_codigo(self):
        codigo = str(self.id)+str(random.randrange(10000, 99999))
        #self.slitrack_codigo = codigo
        self.write({'slitrack_codigo':codigo})

    def action_slitrack_activa(self):
        self.action_slitrack_codigo()
        self.slitrack_estado='noiniciado'
        self.slitrack_st='activo'

class trafitec_slitrack_registro(models.Model):
    _name='tms.slitrack.registro'
    _order='fechahorag desc'
    viaje_id=fields.Many2one(string='Viaje',comodel_name='tms.travel')
    fechahorad=fields.Datetime(string='Fecha hora dispositivo')
    fechahorag=fields.Datetime(string='Fecha hora de generacion')
    latitud=fields.Float(string='Latitud',default=0,digits=(10,10))
    longitud=fields.Float(string='Longitud',default=0,digits=(10,10))
    velocidad=fields.Float(string='Velocidad',default=0,digits=(10,10))
    detalles=fields.Char(string='Detalles',default='')
    proveedor = fields.Selection(string="Tipo", selection=[('slitrack', 'SLI Track'),('manual', 'Manual')],default='manual')

    @api.model
    def create(self,vals):
        return super(trafitec_slitrack_registro, self).create(vals)

    @api.multi
    def unlink(self):
        for r in self:
            if r.proveedor in ("geotab","slitrack"):
                raise UserError(_("Solo se pueden borrar los registros de tipo manual."))
        return super(trafitec_slitrack_registro, self).unlink()

    @api.constrains
    def _validar(self):
        if not self.create_date:
           raise UserError(_("Debe especificar la fecha y hora."))

        if self.latitud == 0 and self.longitud == 0:
            raise UserError(_("Debe especificar la latitud y longitud."))


    def action_vermapa(self):
        return {
        "type": "ir.actions.act_url",
        "url": "http://maps.google.com/maps?q=loc:"+str(self.latitud)+","+str(self.longitud),
        "target": "blank",
        }

class tms_viajes_evidencias(models.Model):
    _name = 'tms.viajes.evidencias'

    name = fields.Selection(string="Tipo",
                            selection=[('Evidencia de viaje', 'Evidencia de viaje'), ('Carta porte', 'Carta porte')],
                            required=True, default='Evidencia de viaje')
    image_filename = fields.Char("Nombre del archivo")
    evidencia_file = fields.Binary(string="Archivo", required=True)
    linea_id = fields.Many2one(comodel_name="tms.travel", string="Evidencia id", ondelete='cascade')


class tms_viajes_boletas(models.Model):
    _name = 'tms.viajes.boletas'

    name = fields.Char(string='Folio de boleta', required=True, track_visibility='onchange')
    tipo_boleta = fields.Selection(string="Tipo de boleta", selection=[('Origen', 'Origen'), ('Destino', 'Destino')],
                                   required=True, track_visibility='onchange')
    linea_id = fields.Many2one(comodel_name="tms.travel", string="Folio de viaje", ondelete='cascade')

    fecha = fields.Date(related='linea_id.fecha_viaje', string='Fecha', store=True, readonly=True)
    cliente = fields.Many2one(related='linea_id.cliente_id', string='Cliente', store=True, readonly=True)
    origen = fields.Many2one(related='linea_id.departure_id', string='Origen', store=True, readonly=True)
    destino = fields.Many2one(related='linea_id.arrival_id', string='Destino', store=True, readonly=True)
    tipo_viaje = fields.Selection(related='linea_id.tipo_viaje', string='Tipo de viaje', store=True, readonly=True)
    state = fields.Selection(related='linea_id.state', string='Estado', store=True, readonly=True)

    @api.model
    def create(self, vals):
        object_boletas = self.env['tms.viajes.boletas'].search([('name', '=ilike', vals['name'])])
        object_viaje = self.env['tms.travel'].search([('id', '=', vals['linea_id'])])

        for object_bolets in object_boletas:
            if vals['tipo_boleta'] == 'Origen':
                if object_viaje.departure_id.id == object_bolets.linea_id.origen.id and object_viaje.cliente_id.id == object_bolets.linea_id.cliente_id.id and object_bolets.tipo_boleta == 'Origen':
                    raise UserError(
                        _('Alerta..\nYa existe un folio para este cliente y bodega de origen.'))
            else:
                if object_viaje.arrival_id.id == object_bolets.linea_id.destino.id and object_viaje.cliente_id.id == object_bolets.linea_id.cliente_id.id and object_bolets.tipo_boleta == 'Destino':
                    raise UserError(
                        _('Alerta..\nYa existe un folio para este cliente y bodega de destino.'))

        return super(tms_viajes_boletas, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'name' in vals:
            name = vals['name']
        else:
            name = self.name
        if 'tipo_boleta' in vals:
            tipo_boleta = vals['tipo_boleta']
        else:
            tipo_boleta = self.tipo_boleta
        object_boletas = self.env['tms.viajes.boletas'].search([('name', '=ilike', name)])
        object_viaje = self.env['tms.travel'].search([('id', '=', self.linea_id.id)])
        for object_bolets in object_boletas:
            if tipo_boleta == 'Origen':
                if object_viaje.departure_id.id == object_bolets.linea_id.origen.id and object_viaje.cliente_id.id == object_bolets.linea_id.cliente_id.id and object_bolets.tipo_boleta == 'Origen':
                    raise UserError(
                        _('Aviso !\nYa existe un folio para este cliente y bodega de origen.'))
            else:
                if object_viaje.arrival_id.id == object_bolets.linea_id.destino.id and object_viaje.cliente_id.id == object_bolets.linea_id.cliente_id.id and object_bolets.tipo_boleta == 'Destino':
                    raise UserError(
                        _('Aviso !\nYa existe un folio para este cliente y bodega de destino.'))

        return super(tms_viajes_boletas, self).write(vals)


class tms_viaje_cargos(models.Model):
    _name = 'tms.viaje.cargos'

    name = fields.Many2one('tms.tipocargosadicionales', string='Tipos de cargos adicionales', required=True)
    valor = fields.Float(string='Valor', required=True)
    line_cargo_id = fields.Many2one('tms.travel', string='Id viaje')
    sistema = fields.Boolean(string="Sistema", default=False)  # Indica si es un registro del sistema.

    @api.constrains('name')
    def _check_name(self):
        obj = self.env['tms.viaje.cargos'].search(
            [('name', '=', self.name.id), ('line_cargo_id', '=', self.line_cargo_id.id)])
        if len(obj) > 1:
            raise UserError(
                _('Aviso !\nNo se puede crear cargos del mismo tipo mas de 1 vez.'))

class tms_tipocargosadicionales(models.Model):
    _name = 'tms.tipocargosadicionales'

    name = fields.Char(string="Nombre", required=True)
    product_id = fields.Many2one('product.product', string='Producto', required=True)

class tms_clasificacionesgxviaje(models.Model):
    _name = 'tms.calificacionesgxviaje'
    viaje_id = fields.Many2one(string='Viaje',comodel_name='tms.travel')
    clasificacion_id = fields.Many2one(string='Calificación',comodel_name='tms.clasificacionesg',required=True)
    operador_nombre = fields.Char(string='Operador',related='viaje_id.employee_id.name',store=True)
    #asociado_nombre = fields.Char(string='Asociado',related='viaje_id.asociado_id.display_name',store=True)
    considerar = fields.Selection(string='Considerado como',related='clasificacion_id.considerar',store=True)

    _sql_constraints = [('viaje_clasificacion_uniq', 'unique(viaje_id, clasificacion_id)', 'La calificación debe ser unica en el viaje.')]

class tms_clasificacionesg(models.Model):
    _name='tms.clasificacionesg'
    name=fields.Char(string='Nombre',default='',required=True)
    aplica_viajes=fields.Boolean(string='Aplica a calificar viaje',default=False)
    considerar=fields.Selection(string="Considerar",selection=[('malo','Malo'),('bueno','Bueno')],default='malo',required=True)
    state=fields.Selection(string='Estado',selection=[('inactivo','Inactivo'),('activo','Activo')],required=True,default='activo')
