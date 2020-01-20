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
import tempfile
import base64
import os


# username = 'javier.ramirez@sli.mx'
# password = 'Javier0318*'
# database = 'GSYEECA'

# geo = mygeotab.API(
#         username=username,
#         password=password,
#         database=database
#     )

# authenticate = geo.authenticate()
def calculate_litres_per_km(from_date, to_date, serial):
    username = 'javier.ramirez@sli.mx'
    password = 'Javier0318*'
    database = 'GSYEECA'
    geo = mygeotab.API(
            username=username,
            password=password,
            database=database
        )
    authenticate = geo.authenticate()
    print(serial)
    xxx = None
    try:
        xxx = geo.get('Device', engineVehicleIdentificationNumber=serial)[0]
    except IndexError:
        xxx = None
    if xxx != None:
        odometer_records = geo.get('StatusData', 
                                      diagnosticSearch=dict(id='DiagnosticOdometerAdjustmentId'),
                                      deviceSearch=dict(id=xxx['id']),
                                      toDate=to_date,
                                      fromDate=from_date)
        fuel_records = geo.get('StatusData',
                                  diagnosticSearch=dict(id='DiagnosticDeviceTotalFuelId'),
                                  deviceSearch=dict(id=xxx['id']),
                                  toDate=to_date,
                                  fromDate=from_date)
        if len(odometer_records) == 0 or len(fuel_records) == 0:
            raise Exception('Device has not travelled in this time period or no fuel usage reported')
        odometer_change = odometer_records[-1]['data'] - odometer_records[0]['data']
        fuel_change = fuel_records[-1]['data'] - fuel_records[0]['data']
        if fuel_change == 0 or odometer_change == 0:
            return 0
        else:
            return fuel_change / (odometer_change / 1000)

class tmstiposcarga(models.Model):
    _name = 'tms.tipos.carga'
    name = fields.Char(string="Nombre", required=True)

    #carga = fields.Selection([('vacio','Vacio'),('medio','Medio'),('pesado','Pesado')])

    costo_sencillo_vacio = fields.Float(string="Costo por km Viaje Sencillo/Vacio")
    costo_doble_vacio = fields.Float(string="Costo por km Viaje Doble/Vacio")
    costo_torton_vacio = fields.Float(string="Costo por km Viaje Tortón/Vacio")
    costo_rabon_vacio = fields.Float(string="Costo por km Viaje Rabón/Vacio")

    costo_sencillo_medido = fields.Float(string="Costo por km Viaje Sencillo/Medido")
    costo_doble_medido = fields.Float(string="Costo por km Viaje Doble/Medido")
    costo_torton_medido = fields.Float(string="Costo por km Viaje Tortón/Medido")
    costo_rabon_medido = fields.Float(string="Costo por km Viaje Rabón/Medido")

    costo_sencillo_pesado = fields.Float(string="Costo por km Viaje Sencillo/Pesado")
    costo_doble_pesado = fields.Float(string="Costo por km Viaje Doble/Pesado")
    costo_torton_pesado = fields.Float(string="Costo por km Viaje Tortón/Pesado")
    costo_rabon_pesado = fields.Float(string="Costo por km Viaje Rabón/Pesado")

    tarifa_sencillo_vacio = fields.Float(string="Tarifa por Viaje Sencillo/Vacio")
    tarifa_doble_vacio = fields.Float(string="Tarifa por Viaje Doble/Vacio")
    tarifa_torton_vacio = fields.Float(string="Tarifa por Viaje Tortón/Vacio")
    tarifa_rabon_vacio = fields.Float(string="Tarifa por Viaje Rabón/Vacio")

    tarifa_sencillo_medido = fields.Float(string="Tarifa por Viaje Sencillo/Medido")
    tarifa_doble_medido = fields.Float(string="Tarifa por Viaje Doble/Medido")
    tarifa_torton_medido = fields.Float(string="Tarifa por Viaje Tortón/Medido")
    tarifa_rabon_medido = fields.Float(string="Tarifa por Viaje Rabón/Medido")

    tarifa_sencillo_pesado = fields.Float(string="Tarifa por Viaje Sencillo/Pesado")
    tarifa_doble_pesado = fields.Float(string="Tarifa por Viaje Doble/Pesado")
    tarifa_torton_pesado = fields.Float(string="Tarifa por Viaje Tortón/Pesado")
    tarifa_rabon_pesado = fields.Float(string="Tarifa por Viaje Rabón/Pesado")

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'El nombre no se puede repetir.'),
    ]

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
    tipo = fields.Selection([('flete','Flete'),('granel','Granel'),('km','Por Kilometro')], string="Tipo", required=True)
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'El nombre no se puede repetir.'),
    ]


class tms_cruce_casetas(models.Model):
    """docstring for tms_cruce_casetas"""
    _name = "tms.cruce.casetas"
    _description = "Tabla para comparar el cruce de las casetas del viaje"
    name = fields.Char(string="Cruce")
    unidad = fields.Char(string="Unidad")
    fecha = fields.Char(string="Fecha")
    hora = fields.Char(string="Hora")
    caseta = fields.Char(string="Caseta")
    caseta_id = fields.Many2one("tms.route.tollstation", string="Caseta", compute="_compute_caseta")
    travel_id = fields.Many2one("tms.travel", string="Viaje")
    travel2_id = fields.Many2one("tms.travel", string="Viaje")
    travel3_id = fields.Many2one("tms.travel", string="Viaje")
    marcada = fields.Boolean(default=False)

    @api.one
    def _compute_caseta(self):
        objcaseta = self.env['tms.route.tollstation'].search([])
        for x in objcaseta:
            nom = str(x.name).upper()
            if nom == str(self.caseta):
                self.caseta_id = x.id

class TmsTravel(models.Model):
    _name = 'tms.travel'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Travel'
    _order = "date desc"


    #cambios victor
    travels_id = fields.Many2one("tms.travel", string="Origen")
    facturar = fields.Boolean(string="No Facturable", default=False)
    validar_viaje=fields.Boolean(string='Validar Viaje' )

    @api.onchange('unit_id.insurance_days_to_expire','travel_duration')
    def onchange_validar_viaje(self):
        duration=self.travel_duration/24

        if self.unit_id.insurance_days_to_expire < duration:
            self.validar_viaje=True
        else:
            self.validar_viaje=False 

    kml_ex = fields.Boolean(string="Kilometros Extra", default=False)
    kmlextra = fields.Float(string="KM")
    kml_ex2 = fields.Boolean(string="Kilometros Extra", default=False)
    kmlextra2 = fields.Float(string="KM")

    #

    #Agregando campos
    file_casetas = fields.Binary(string="Archivo de casetas.")
    filename = fields.Char('file name')

    cruce_casetas = fields.One2many("tms.cruce.casetas","travel_id")
    cruce_casetas_planeado = fields.One2many("tms.cruce.casetas","travel2_id")
    cruce_casetas_faltantes = fields.One2many("tms.cruce.casetas","travel3_id")



    @api.onchange('file_casetas','unit_id')
    def onchange_file_casetas(self):
        if self.file_casetas and self.unit_id:
            data = base64.decodestring(self.file_casetas)
            fobj = tempfile.NamedTemporaryFile(delete=False)
            fname = fobj.name
            fobj.write(data)
            fobj.close()
            image = open(fname,"r")
            cont = 0
            line_ids = []
            res = {'value':{
                    'cruce_casetas':[],
                }
            }
            for x in image:
                lista = x.split("|")
                ll = x.split(",")
                if ll[0] == 'Tag' or ll[0] == '\r\n':
                    print(ll)
                else:
                    print(lista)
                    nom = lista[4]
                    cc = 0
                    for z in nom:
                        if z.isdigit():
                            nom = nom[0:cc-1]
                            break
                        cc += 1


                    if self.unit_id.name == lista[1]:
                        line = {
                          'name': lista[0],
                          'unidad': lista[1],
                          'fecha': lista[2],
                          'hora': lista[3],
                          'caseta': nom,
                          'travel_id': self.id,
                        }
                        line_ids += [line]
            res['value'].update({
                'cruce_casetas': line_ids,
            })
            return res
        else:
            line_ids = []
            res = {'value':{
                    'cruce_casetas':[],
                }
            }
            return res

    @api.onchange('route_id','route2_id','file_casetas')
    def onchange_casetas_plan(self):
        line_ids = []
        res = {'value':{
                'cruce_casetas_planeado':[],
            }
        }
        if self.route_id:
            for x in self.route_id.tollstation_ids:
                if x.credit == True:
                    line = {
                      'name':"Ruta - " + x.name,
                      'unidad': self.unit_id.name,
                      'caseta': str(x.name).upper(),
                      'travel2_id': self.id,
                    }
                    line_ids += [line]
        if self.route2_id:
            for x in self.route2_id.tollstation_ids:
                if x.credit == True:
                    line = {
                      'name':"Ruta - " + x.name,
                      'unidad': self.unit_id.name,
                      'caseta': str(x.name).upper(),
                      'travel2_id': self.id,
                    }
                    line_ids += [line]
        res['value'].update({
            'cruce_casetas_planeado': line_ids,
        })
        return res

    @api.onchange('cruce_casetas','cruce_casetas_planeado','file_casetas')
    def onchange_casetas_real(self):
        for x in self.cruce_casetas:
            if x.marcada != True:
                for z in self.cruce_casetas_planeado:
                    if z.marcada != True:
                        if x.caseta_id == z.caseta_id:
                            x.marcada = True
                            z.marcada = True
        line_ids = []
        res = {'value':{
                'cruce_casetas_faltantes':[],
            }
        }
        for y in self.cruce_casetas_planeado:
            if y.marcada != True:
                
                line = {
                  'name':y.name,
                  'unidad': self.unit_id.name,
                  'caseta': y.caseta,
                  'travel3_id': self.id,
                }
                line_ids += [line]
        res['value'].update({
            'cruce_casetas_faltantes': line_ids,
        })
        return res



    waybill_ids = fields.Many2many(
        'tms.waybill', string='Waybills')
    driver_factor_ids = fields.One2many(
        'tms.factor', 'travel_id', string='Travel Driver Payment Factors')
    name = fields.Char('Travel Number')
    state = fields.Selection([
        ('draft', 'Pendiente'), ('progress', 'En progreso'), ('done', 'Hecho'),
        ('cancel', 'Cancelado'), ('closed', 'Cerrado')],
        readonly=True, default='draft')
    route_id = fields.Many2one(
        'tms.route', 'Route', required=True,
        states={'cancel': [('readonly', True)],
                'closed': [('readonly', True)]})
    route2_id = fields.Many2one(
        'tms.route', '2da Ruta',
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
    fuel_efficiency_expected = fields.Float()

    @api.onchange('unit_id','rendimiento_manual1','rendimiento_manual2','kmlmuno','kmlm2')
    def _onchange_fuel_efficiency_expected(self):
        if self.rendimiento_manual1 != True and self.rendimiento_manual2 != True:
            self.fuel_efficiency_expected = self.unit_id.efficiency
        if self.rendimiento_manual1 == True and self.rendimiento_manual2 != True:
            self.fuel_efficiency_expected = (self.unit_id.efficiency + self.kmlmuno)/2
        if self.rendimiento_manual1 != True and self.rendimiento_manual2 == True:
            self.fuel_efficiency_expected = (self.unit_id.efficiency + self.kmlm2)/2
        if self.rendimiento_manual1 == True and self.rendimiento_manual2 == True:
            self.fuel_efficiency_expected = (self.kmlm2 + self.kmlmuno)/2

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
        'hr.employee', 'Driver',
        domain=[('driver', '=', True)], store=True)




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
    departure2_id = fields.Many2one(
        'tms.place',
        string='2do Origen',
        compute='_compute_departure2_id',
        store=True,
        readonly=True)
    fuel_log_ids = fields.One2many(
        'fleet.vehicle.log.fuel', 'travel_id', string='Fuel Vouchers', readonly=True)
    advance_ids = fields.One2many(
        'tms.advance', 'travel_id', string='Advances')
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
    expense_id = fields.Many2one(
        'tms.expense', 'Expense Record', readonly=True)
    account_id = fields.Many2one(
        'account.invoice', 'Registro de Factura', readonly=True)
    event_ids = fields.One2many('tms.event', 'travel_id', string='Events')
    is_available = fields.Boolean(
        compute='_compute_is_available',
        string='Travel available')
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit',default=lambda self: self.env['operating.unit'].search([('name','=','Mexico')], limit=1).id or self.env['operating.unit'].search([('name','=','México')], limit=1).id or '')
    color = fields.Integer()
    framework = fields.Selection([
        ('unit', 'Unit'),
        ('single', 'Single'),
        ('double', 'Double')],
        compute='_compute_framework')
    partner_ids = fields.Many2many(
        'res.partner', string='Customer', compute='_compute_partner_ids',
        store=True)


    fecha_viaje = fields.Date(string='Fecha del viaje', readonly=False, index=True, copy=False,
                              default=fields.Datetime.now, required=True)
    subpedido_id = fields.Many2one('sale.order', string='Cotización', change_default=True, index=True, track_visibility='always')
    product = fields.One2many('sale.order.line', string='Producto', related="subpedido_id.order_line")

    producto = fields.Many2one("product.template", string="Producto a transportar",required=True)
    costo_producto = fields.Float(string='Costo del producto', track_visibility='onchange', readonly=True, related="producto.standard_price")
    sucursal_id = fields.Many2one('tms.sucursal', string='Sucursal', required=True, track_visibility='onchange',default=lambda self: self.env['tms.sucursal'].search([('name','=','Patio Central')], limit=1).id or '')
    cliente_id = fields.Many2one('res.partner', string="Cliente", required=True, track_visibility='onchange')
    tarifa_cliente = fields.Float(string='Tarifa cliente 1', default=0,required=True)
    tarifa_cliente2 = fields.Float(string='Tarifa cliente 2', default=0,required=True)
    celular_operador = fields.Char(string='Celular operador', readonly=True, related="employee_id.mobile_phone")
    tipo_viaje = fields.Selection([('Normal', 'Normal'), ('Directo', 'Directo'), ('Cobro destino', 'Cobro destino')],
                                  string='Tipo de viaje', default='Normal', required=True)
    tipo_remolque = fields.Selection([('sencillo','Sencillo'),('doble','Doble'),('torton','Tortón'),('rabon','Rabón')], string="Tipo de remolque", required=True)
    tipo_carga = fields.Many2one("tms.tipos.carga", string="Tipo Carga", required=True)
    lineanegocio = fields.Many2one(comodel_name='tms.lineanegocio', string='Linea de negocios', store=True)
    tipo_negocio = fields.Selection([('flete','Flete'),('granel','Granel'),('km','Por Kilometro')], string="Tipo", related='lineanegocio.tipo', required=True)
    tipo_lineanegocio = fields.Char('Tipo de linea de negocio', related='lineanegocio.name', store=True)
    flete_cliente = fields.Float(string='Flete cliente', readonly=True, compute='_compute_flete_cliente')
    flete_1 = fields.Float(string='Flete cliente', readonly=True, compute='_compute_flete_cliente1')
    flete_2 = fields.Float(string='Flete cliente', readonly=True, compute='_compute_flete_cliente2')

    @api.onchange('unit_id')
    def onchange_unit_employee_id(self):
        self.employee_id = self.unit_id.employee_id.id

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.celular_operador = self.employee_id.mobile_phone

    @api.constrains('lineanegocio', 'sucursal_id',
                    'peso_origen_remolque_1', 'peso_origen_remolque_2', 'peso_destino_remolque_1',
                    'peso_destino_remolque_2', 'peso_convenido_remolque_1', 'peso_convenido_remolque_2')
    def _valida(self):
        if not self.lineanegocio:
            raise UserError(_('Alerta !\nDebe especificar la línea de negocio.'))

        if not self.sucursal_id:
            raise UserError(_('Alerta !\nDebe especificar la sucursal.'))

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

    @api.onchange('tipo_carga','modalidad_ruta1','modalidad_ruta2','lineanegocio','tipo_remolque','route_id','route2_id')
    def onchange_tipo_carga(self):
        if self.lineanegocio.tipo == 'km' and self.modalidad_ruta1 == 'vacio':
            if self.tipo_remolque == 'sencillo':
                self.tarifa_cliente = self.tipo_carga.costo_sencillo_vacio
            if self.tipo_remolque == 'doble':
                self.tarifa_cliente = self.tipo_carga.costo_doble_vacio
            if self.tipo_remolque == 'torton':
                self.tarifa_cliente = self.tipo_carga.costo_torton_vacio
            if self.tipo_remolque == 'rabon':
                self.tarifa_cliente = self.tipo_carga.costo_rabon_vacio
        if self.lineanegocio.tipo == 'km' and self.modalidad_ruta1 == 'medido':
            if self.tipo_remolque == 'sencillo':
                self.tarifa_cliente = self.tipo_carga.costo_sencillo_medido
            if self.tipo_remolque == 'doble':
                self.tarifa_cliente = self.tipo_carga.costo_doble_medido
            if self.tipo_remolque == 'torton':
                self.tarifa_cliente = self.tipo_carga.costo_torton_medido
            if self.tipo_remolque == 'rabon':
                self.tarifa_cliente = self.tipo_carga.costo_rabon_medido
        if self.lineanegocio.tipo == 'km' and self.modalidad_ruta1 == 'pesado':
            if self.tipo_remolque == 'sencillo':
                self.tarifa_cliente = self.tipo_carga.costo_sencillo_pesado
            if self.tipo_remolque == 'doble':
                self.tarifa_cliente = self.tipo_carga.costo_doble_pesado
            if self.tipo_remolque == 'torton':
                self.tarifa_cliente = self.tipo_carga.costo_torton_pesado
            if self.tipo_remolque == 'rabon':
                self.tarifa_cliente = self.tipo_carga.costo_rabon_pesado
        if not self.route2_id:
            self.tarifa_cliente2 = 0
        if self.route2_id:
            if self.lineanegocio.tipo == 'km' and self.modalidad_ruta2 == 'vacio':
                if self.tipo_remolque == 'sencillo':
                    self.tarifa_cliente2 = self.tipo_carga.costo_sencillo_vacio
                if self.tipo_remolque == 'doble':
                    self.tarifa_cliente2 = self.tipo_carga.costo_doble_vacio
                if self.tipo_remolque == 'torton':
                    self.tarifa_cliente2 = self.tipo_carga.costo_torton_vacio
                if self.tipo_remolque == 'rabon':
                    self.tarifa_cliente2 = self.tipo_carga.costo_rabon_vacio
            if self.lineanegocio.tipo == 'km' and self.modalidad_ruta2 == 'medido':
                if self.tipo_remolque == 'sencillo':
                    self.tarifa_cliente2 = self.tipo_carga.costo_sencillo_medido
                if self.tipo_remolque == 'doble':
                    self.tarifa_cliente2 = self.tipo_carga.costo_doble_medido
                if self.tipo_remolque == 'torton':
                    self.tarifa_cliente2 = self.tipo_carga.costo_torton_medido
                if self.tipo_remolque == 'rabon':
                    self.tarifa_cliente2 = self.tipo_carga.costo_rabon_medido
            if self.lineanegocio.tipo == 'km' and self.modalidad_ruta2 == 'pesado':
                if self.tipo_remolque == 'sencillo':
                    self.tarifa_cliente2 = self.tipo_carga.costo_sencillo_pesado
                if self.tipo_remolque == 'doble':
                    self.tarifa_cliente2 = self.tipo_carga.costo_doble_pesado
                if self.tipo_remolque == 'torton':
                    self.tarifa_cliente2 = self.tipo_carga.costo_torton_pesado
                if self.tipo_remolque == 'rabon':
                    self.tarifa_cliente2 = self.tipo_carga.costo_rabon_pesado

    @api.one
    @api.depends('lineanegocio','peso_origen_total','tarifa_cliente','tarifa_cliente2','facturar_con_cliente','peso_convenido_total','peso_origen_total','peso_destino_total','kmlextra','kmlextra2')
    def _compute_flete_cliente(self):
        for reg in self:
            if self.lineanegocio.tipo == 'granel':
                if reg.facturar_con_cliente == 'Peso convenido':
                    reg.flete_cliente = ((reg.peso_convenido_total / 1000) * reg.tarifa_cliente) + ((reg.peso_convenido_total / 1000) * reg.tarifa_cliente2)
                elif reg.facturar_con_cliente == 'Peso origen':
                    reg.flete_cliente = ((reg.peso_origen_total / 1000) * reg.tarifa_cliente) + ((reg.peso_origen_total / 1000) * reg.tarifa_cliente2)
                elif reg.facturar_con_cliente == 'Peso destino':
                    reg.flete_cliente = ((reg.peso_destino_total / 1000) * reg.tarifa_cliente) + ((reg.peso_destino_total / 1000) * reg.tarifa_cliente2)
            if self.lineanegocio.tipo == 'flete':
                reg.flete_cliente = reg.tarifa_cliente + reg.tarifa_cliente2
            if self.lineanegocio.tipo == 'km':
                if self.kmlextra > 0 or self.kmlextra2 > 0:
                    reg.flete_cliente = (reg.tarifa_cliente * (self.route_id.distance + self.kmlextra)) + (reg.tarifa_cliente2 * (self.route2_id.distance+self.kmlextra2))
                else:
                    reg.flete_cliente = (reg.tarifa_cliente * (self.route_id.distance)) + (reg.tarifa_cliente2 * (self.route2_id.distance))
               

    @api.one
    @api.depends('lineanegocio','peso_origen_total','tarifa_cliente','tarifa_cliente2','facturar_con_cliente','peso_convenido_total','peso_origen_total','peso_destino_total')
    def _compute_flete_cliente1(self):
        for reg in self:
            if self.lineanegocio.tipo == 'granel':
                if reg.facturar_con_cliente == 'Peso convenido':
                    reg.flete_1 = ((reg.peso_convenido_total / 1000) * reg.tarifa_cliente) 
                elif reg.facturar_con_cliente == 'Peso origen':
                    reg.flete_1 = ((reg.peso_origen_total / 1000) * reg.tarifa_cliente)
                elif reg.facturar_con_cliente == 'Peso destino':
                    reg.flete_1 = ((reg.peso_destino_total / 1000) * reg.tarifa_cliente)
            if self.lineanegocio.tipo == 'flete':
                reg.flete_1 = reg.tarifa_cliente
            if self.lineanegocio.tipo == 'km':
                reg.flete_1 = (reg.tarifa_cliente * (self.route_id.distance))

    @api.one
    @api.depends('lineanegocio','peso_origen_total','tarifa_cliente','tarifa_cliente2','facturar_con_cliente','peso_convenido_total','peso_origen_total','peso_destino_total')
    def _compute_flete_cliente2(self):
        for reg in self:
            if self.lineanegocio.tipo == 'granel':
                if reg.facturar_con_cliente == 'Peso convenido':
                    reg.flete_2 = ((reg.peso_convenido_total / 1000) * reg.tarifa_cliente2) 
                elif reg.facturar_con_cliente == 'Peso origen':
                    reg.flete_2 = ((reg.peso_origen_total / 1000) * reg.tarifa_cliente2)
                elif reg.facturar_con_cliente == 'Peso destino':
                    reg.flete_2 = ((reg.peso_destino_total / 1000) * reg.tarifa_cliente2)
            if self.lineanegocio.tipo == 'flete':
                reg.flete_2 = reg.tarifa_cliente2
            if self.lineanegocio.tipo == 'km':
                reg.flete_2 = (reg.tarifa_cliente2 * (self.route2_id.distance))

    
    @api.onchange('route_id','route2_id')
    def onchange_flete_cliente(self):
        for reg in self:
            if self.lineanegocio.tipo == 'granel':
                if reg.facturar_con_cliente == 'Peso convenido':
                    reg.flete_2 = (reg.peso_convenido_total / 1000) * reg.tarifa_cliente2
                elif reg.facturar_con_cliente == 'Peso origen':
                    reg.flete_2 = (reg.peso_origen_total / 1000) * reg.tarifa_cliente2
                elif reg.facturar_con_cliente == 'Peso destino':
                    reg.flete_2 = (reg.peso_destino_total / 1000) * reg.tarifa_cliente2
            if self.lineanegocio.tipo == 'flete':
                reg.flete_2 = reg.tarifa_cliente2
            if self.lineanegocio.tipo == 'km':
                reg.flete_2 = reg.tarifa_cliente2 * (self.route_id.distance + self.route2_id.distance)

    #@api.onchange('driver_factor_ids','com_necesario')
    @api.onchange('driver_factor_ids')
    def onchange_flete_cliente_anticipo(self):
        """
        line_ids = []
        for x in self.advance_ids:
            if x.advance_auto != True:
                line = {
                  'id': x.id,
                  'name':x.name,
                  'operating_unit_id': x.operating_unit_id.id,
                  'unit_id': x.unit_id.id,
                  'product_id': x.product_id.id,
                  'employee_id': x.employee_id.id,
                  'amount': x.amount,
                  'currency_id': x.currency_id,
                  'date':x.date,
                  'notes': x.notes,
                  'state':x.state,
                  'move_id':x.move_id.id,
                  'expense_id':x.expense_id.id,
                  'cuenta_b':x.cuenta_b.id,
                  'adjunto_compro':x.adjunto_compro,
                  'paid':x.paid,
                  'payment_move_id':x.payment_move_id.id,
                  'n_transaccion':x.n_transaccion,
                  'auto_expense':x.auto_expense,
                }
                line_ids += [line]
        
        res = {'value':{
                'advance_ids':[],
            }
        }
        if self.driver_factor_ids:
            
            comb = self.env['product.product'].search([('tms_product_category','=','real_expense')], limit=1)
            total = 0
            for x in self.driver_factor_ids:
                if x.factor_type == 'costo_fijo':
                    total = x.valor
                if x.factor_type == 'porcentaje':
                    total = (self.flete_cliente/100) * x.valor
                if x.factor_type == 'costokm':
                    d1 = 0
                    d2 = 0
                    if self.kml_ex == True:
                        d1 = self.kmlextra
                    if self.kml_ex2 == True:
                        d1 = self.kmlextra2
                    if x.if_diferentes != True:
                        total = x.valor * (self.route_id.distance + d1 + self.route2_id.distance + d2)
                    if x.if_diferentes == True:
                        total = (x.valor * self.route_id.distance + d1) + (x.valor2 * self.route2_id.distance + d2)

                line = {
                  'operating_unit_id': self.operating_unit_id.id,
                  'unit_id': self.unit_id.id,
                  'product_id': comb.id,
                  'employee_id': self.employee_id.id,
                  'amount': total * 0.2,
                  'currency_id': self.env.user.company_id.currency_id,
                  'date':datetime.today(),
                  'notes': "Monto generado automaticamente calculando el 20 porciento del factor del operador",
                  'state':'draft',
                  'adelanto_factor': True,
                  'advance_auto': True,
                }
            line_ids += [line]


        product_caseta_obj = self.env['product.product'].search([('es_caseta','=',True)], limit=1)
        suma = 0
        for x in self.route_id.tollstation_ids:
            for z in x.cost_per_axis_ids:
                if z.axis == self.ejes:
                    if not x.credit == True:
                        suma += z.cost_cash
        for x in self.route2_id.tollstation_ids:
            for z in x.cost_per_axis_ids:
                if z.axis == self.ejes:
                    if not x.credit == True:
                        suma += z.cost_cash
        if suma > 0:
            line = {
              'operating_unit_id': self.operating_unit_id.id,
              'unit_id': self.unit_id.id,
              'product_id': product_caseta_obj.id,
              'employee_id': self.employee_id.id,
              'amount': suma,
              'currency_id': self.env.user.company_id.currency_id,
              'date':datetime.today(),
              'notes': "Monto generado automaticamente para pagar casetas sin opcion de credito activa",
              'state':'draft',
              'advance_auto': True,
            }
            line_ids += [line]

        res['value'].update({
            'advance_ids': line_ids,
        })
        return res
        """
        todos_ids = []
        existentes_ids = []
        otros_ids = []
        #---------------------------------
        #ANTICIPOS EXISTENTES
        #---------------------------------
        #tipo: 1=Actualizar,0=Crear
        for x in self.advance_ids:
            line = {
                'tipo': 1,
                'id': x.id,
                'datos':
                    {
              'name': str(x.name or ''),
              'operating_unit_id': x.operating_unit_id.id,
              'unit_id': x.unit_id.id,
              'product_id': x.product_id.id,
              'employee_id': x.employee_id.id,
              'amount': x.amount,
              'currency_id': x.currency_id.id,
              'date': x.date,
              'notes': str(x.notes or ''),
              'state': x.state,
              'move_id': x.move_id.id,
              'expense_id': x.expense_id.id,
              'travel_id': x.travel_id.id,
              'cuenta_b': x.cuenta_b.id,
              'adjunto_compro': x.adjunto_compro,
              'paid': x.paid,
              'payment_move_id': x.payment_move_id.id,
              'n_transaccion': x.n_transaccion,
              'auto_expense': x.auto_expense,
              'advance_auto': x.advance_auto
              }
            }
            existentes_ids.append(line)
            
        
            
        #---------------------------------
        #FACTORES
        #---------------------------------
        if self.driver_factor_ids:
            comb = self.env['product.product'].search([('tms_product_category', '=', 'real_expense')], limit=1)
            total = 0
            for x in self.driver_factor_ids:
                if x.factor_type == 'costo_fijo':
                    total = x.valor
                if x.factor_type == 'porcentaje':
                    total = (self.flete_cliente/100) * x.valor
                if x.factor_type == 'costokm':
                    d1 = 0
                    d2 = 0
                    if self.kml_ex == True:
                        d1 = self.kmlextra
                    if self.kml_ex2 == True:
                        d1 = self.kmlextra2
                    if x.if_diferentes != True:
                        total = x.valor * (self.route_id.distance + d1 + self.route2_id.distance + d2)
                    if x.if_diferentes == True:
                        total = (x.valor * self.route_id.distance + d1) + (x.valor2 * self.route2_id.distance + d2)

                line = {
                  'tipo': 1,
                  'id': 0,
                  'datos': {
                    'operating_unit_id': self.operating_unit_id.id,
                    'unit_id': self.unit_id.id,
                    'product_id': comb.id,
                    'employee_id': self.employee_id.id,
                    'amount': total * 0.2,
                    'currency_id': self.env.user.company_id.currency_id,
                    'date': datetime.today(),
                    'notes': "Monto generado automaticamente calculando el 20 porciento del factor del operador",
                    'state': 'draft',
                    'adelanto_factor': True,
                    'advance_auto': True,
                  }
                }

                existe = False
                for ant in existentes_ids:
                    if comb.id == ant['datos']['product_id'] and ant['datos']['advance_auto']:
                        existe = True
                        ant.update({'datos': line['datos']})
                
                """
                if not existe:
                    line.update({'tipo': 0})
                    existentes_ids.append(line)
                """        
        
        #todos_ids.append(existentes_ids)
        #todos_ids += otros_ids
        
        #---------------------------------
        #RUTA 1 Y 2
        #---------------------------------
        product_caseta_obj = self.env['product.product'].search([('es_caseta', '=', True)], limit=1)
        suma = 0
        
        for x in self.route_id.tollstation_ids:
            for z in x.cost_per_axis_ids:
                if z.axis == self.ejes:
                    if not x.credit == True:
                        suma += z.cost_cash
        
        for x in self.route2_id.tollstation_ids:
            for z in x.cost_per_axis_ids:
                if z.axis == self.ejes:
                    if not x.credit == True:
                        suma += z.cost_cash
        
        if suma > 0:
            line = {
                'tipo': 1,
                'datos': {
              'operating_unit_id': self.operating_unit_id.id,
              'unit_id': self.unit_id.id,
              'product_id': product_caseta_obj.id,
              'employee_id': self.employee_id.id,
              'amount': suma,
              'currency_id': self.env.user.company_id.currency_id,
              'date': datetime.today(),
              'notes': "Monto generado automaticamente para pagar casetas sin opcion de credito activa",
              'state': 'draft',
              'advance_auto': True,
              }
            }
            existe = False
            for ant in existentes_ids:
                if product_caseta_obj.id == ant['datos']['product_id'] and ant['datos']['advance_auto']:
					existe = True
					if ant['datos']['state'] != 'confirmed':
						ant.update({'datos': line['datos']})

            if not existe:
                line.update({'tipo': 0})
                existentes_ids.append(line)
        
        #------------------------------------
        #REALIZA LAS TAREAS FINALES
        #------------------------------------
        final_ids = []                      
        for i in existentes_ids:
            if i['tipo'] == 1:
                final_ids += [(i['tipo'], i['id'], i['datos'])]
            if i['tipo'] == 0:
                final_ids += [(0, 0, i['datos'])]
                
        #---------------------------------
        #ACTUALIZAR
        #---------------------------------
        self.update({'advance_ids': final_ids})
    
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
        else:
            self.merma_cobrar_pesos = 0

    merma_cobrar_pesos = fields.Float(string='Merma cobrar $', readonly=True, compute="_compute_merma_cobrar_pesos")

    tipo_viaje = fields.Selection([('Normal', 'Normal'), ('Directo', 'Directo'), ('Cobro destino', 'Cobro destino')],
                                  string='Tipo de viaje', default='Normal', required=True)

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

    @api.depends('route2_id')
    def _compute_departure2_id(self):
        for rec in self:
            rec.departure2_id = rec.route2_id.departure_id

    @api.depends('route2_id')
    def _compute_arrival2_id(self):
        for rec in self:
            rec.arrival2_id = rec.route2_id.arrival_id

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

    @api.onchange('route_id','route2_id','modalidad_ruta1','modalidad_ruta2', 'kmlextra','kmlextra2')
    def _onchange_route(self):
        self.travel_duration = self.route_id.travel_time + self.route2_id.travel_time
        self.distance_route = self.route_id.distance + self.route2_id.distance + self.kmlextra + self.kmlextra2
        cargado = 0
        vacio = 0
        if self.modalidad_ruta1 != 'vacio':
            cargado += self.route_id.distance_loaded
            vacio += self.route_id.distance_empty
        if self.route2_id and self.modalidad_ruta2 != 'vacio':
            cargado += self.route2_id.distance_loaded
            vacio += self.route_id.distance_empty

        self.distance_loaded = cargado
        
        if self.modalidad_ruta1 == 'vacio':
            vacio += self.route_id.distance
        if self.route2_id and self.modalidad_ruta2 == 'vacio':
            vacio += self.route2_id.distance
        self.distance_empty = vacio

    @api.depends('distance_empty', 'distance_loaded')
    def _compute_distance_driver(self):
        for rec in self:
            rec.distance_driver = rec.distance_empty + rec.distance_loaded

    @api.multi
    def action_draft(self):
        for rec in self:
            rec.state = "draft"
    odometro_inicial = fields.Float("Odometro Inicial")
    odometro_final = fields.Float("Odometro Final")

    @api.onchange('unit_id','route_id','route2_id','distance_driver')
    def _onchange_odo_inicial(self):
        for rec in self:
            rec.odometro_inicial = rec.unit_id.odometer
            rec.odometro_final = rec.unit_id.odometer + rec.distance_driver

    @api.multi
    def action_progress(self):
        for rec in self:
            #victor
            if self.validar_viaje==True:
                raise ValidationError(
                    _('La Póliza expira antes de terminar el viaje'))
            fec_ac= str (datetime.now (). date ())

            dato = self.env['fleet.vehicle.red_tape'].search([('vehicle_id','=',self.unit_id.id),('date_end','<=',fec_ac)])
            fec=dato.date_end
            pror=dato.dias
            for l in dato:
                if l.prorroga==True:
                    continue
                    # cur_date = str(l.date_end)
                    # new_date = cur_date + timedelta(days=5)      
                    # if new_date <= fec_ac:
                    #     raise ValidationError(
                    #         _("se encuentra vencido el tramite: %s" % l.name))
                if l.date_end <= fec_ac:
                        raise ValidationError(
                            _("se encuentra vencido el tramite: %s" % l.name))
            #
            if not self.subpedido_id:
                raise ValidationError(
                    _('Aun no hay un pedido asociado'))
            if self.subpedido_id.state not in ['sale','done']:
                raise ValidationError(
                    _('El pedido no esta autorizado'))
            val = True
            for x in self.fuel_log_ids:
                if x.state != 'approved' and x.state != 'confirmed':
                    val = False
            if val == False:
                raise ValidationError(
                    _('Uno o mas vales aun no son aprovados o confirmados'))
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
            rec.odometro_inicial = rec.unit_id.odometer
            rec.odometro_final = rec.unit_id.odometer + rec.distance_driver
            rec.message_post('Travel Dispatched')


    

    @api.multi
    def action_done(self):
        ahora = fields.Datetime.now()
        if self.unit_id.serial_number:
            self.fuel_efficiency_travel = calculate_litres_per_km(self.date_start_real, ahora, str(self.unit_id.serial_number))
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
            rec.date_end_real = ahora
            rec.message_post('Travel Finished')


    # @api.depends('route_id','fuel_log_ids')
    # @api.onchange('route_id')
    # def _onchange_ruta_fuel(self):
    #     line_ids = []
    #     res = {'value':{
    #             'fuel_log_ids':[],
    #         }
    #     }
    #     for x in self.route_id.fuel_log_ids:
    #         lines = {
    #           'operating_unit_id': self.operating_unit_id.id,
    #           'vendor_id': x.vendor_id.id,
    #           'vehicle_id': self.unit_id.id,
    #           'date': datetime.today(),
    #           'product_id': x.product_id,
    #           'product_qty': x.product_qty,
    #           'state': 'approved',
    #         }
    #         line_ids += [lines]
    #     res['value'].update({
    #         'fuel_log_ids': line_ids,
    #     })
    #     return res

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
        print(values.get('com_solicitado'))
        print(values.get('com_necesario'))
        if values.get('com_solicitado') > values.get('com_necesario'):
            raise UserError(
                _('Aviso !\nLa suma en los vales de combustible ('+'{0:.2f}'.format(values.get('com_solicitado'))+' Litros) es mayor al necesario. (' + '{0:.2f}'.format(values.get('com_necesario')) + ' Litros)'))
        
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
        self.write({'slitrack_codigo':codigo})

    def action_slitrack_activa(self):
        self.action_slitrack_codigo()
        self.slitrack_estado='noiniciado'
        self.slitrack_st='activo'


    ejes = fields.Integer(string="Total de ejes.", compute="_total_ejes")
    costo_casetas = fields.Float(string="Costo Total de Casetas", compute="_costo_casetas")
    casetas1 = fields.Float(string="Costo de Casetas Ruta 1", compute="_costo_casetas1")
    casetas2 = fields.Float(string="Costo de Casetas Ruta 2", compute="_costo_casetas2")

    @api.one
    def _total_ejes(self):
        if self.tipo_remolque == 'doble':
            self.ejes = self.unit_id.ejes + self.trailer1_id.ejes + self.dolly_id.ejes + self.trailer2_id.ejes
        else:
            self.ejes = self.unit_id.ejes + self.trailer1_id.ejes
        if self.tipo_remolque != 'doble':
            self.dolly_id = ''
            self.trailer2_id = ''

    @api.onchange('tipo_remolque','unit_id','trailer1_id','dolly_id','trailer2_id')
    def _onchange_total_ejes(self):
        if self.tipo_remolque == 'doble':
            self.ejes = self.unit_id.ejes + self.trailer1_id.ejes + self.dolly_id.ejes + self.trailer2_id.ejes
        else:
            self.ejes = self.unit_id.ejes + self.trailer1_id.ejes
        if self.tipo_remolque != 'doble':
            self.dolly_id = ''
            self.trailer2_id = ''

    @api.one
    def _costo_casetas(self):
        suma = 0
        for x in self.route_id.tollstation_ids:
            for z in x.cost_per_axis_ids:
                if z.axis == self.ejes:
                    if x.credit == True:
                        suma += z.cost_credit
                    if not x.credit == True:
                        suma += z.cost_cash
        for x in self.route2_id.tollstation_ids:
            for z in x.cost_per_axis_ids:
                if z.axis == self.ejes:
                    if x.credit == True:
                        suma += z.cost_credit
                    if not x.credit == True:
                        suma += z.cost_cash
        self.costo_casetas = suma

    @api.one
    def _costo_casetas1(self):
        suma = 0
        for x in self.route_id.tollstation_ids:
            for z in x.cost_per_axis_ids:
                if z.axis == self.ejes:
                    if x.credit == True:
                        suma += z.cost_credit
                    if not x.credit == True:
                        suma += z.cost_cash
        self.casetas1 = suma

    @api.one
    def _costo_casetas2(self):
        suma = 0
        for x in self.route2_id.tollstation_ids:
            for z in x.cost_per_axis_ids:
                if z.axis == self.ejes:
                    if x.credit == True:
                        suma += z.cost_credit
                    if not x.credit == True:
                        suma += z.cost_cash
        self.casetas2 = suma

    @api.onchange('route_id','route2_id','ejes')
    def _onchange_costo_casetas(self):
        suma = 0
        for x in self.route_id.tollstation_ids:
            for z in x.cost_per_axis_ids:
                if z.axis == self.ejes:
                    if x.credit == True:
                        suma += z.cost_credit
                    if not x.credit == True:
                        suma += z.cost_cash
        for x in self.route2_id.tollstation_ids:
            for z in x.cost_per_axis_ids:
                if z.axis == self.ejes:
                    if x.credit == True:
                        suma += z.cost_credit
                    if not x.credit == True:
                        suma += z.cost_cash
        self.costo_casetas = suma

    @api.onchange('route_id','ejes')
    def _onchange_costo_casetas1(self):
        suma = 0
        for x in self.route_id.tollstation_ids:
            for z in x.cost_per_axis_ids:
                if z.axis == self.ejes:
                    if x.credit == True:
                        suma += z.cost_credit
                    if not x.credit == True:
                        suma += z.cost_cash
        self.casetas1 = suma

    @api.onchange('route2_id','ejes')
    def _onchange_costo_casetas2(self):
        suma = 0
        for x in self.route2_id.tollstation_ids:
            for z in x.cost_per_axis_ids:
                if z.axis == self.ejes:
                    if x.credit == True:
                        suma += z.cost_credit
                    if not x.credit == True:
                        suma += z.cost_cash
        self.casetas2 = suma

    

    kml = fields.Float(string="KM/L", compute="_comp_fuel_kml")
    com_necesario = fields.Float(string="Combustible necesario")
    combustible1 = fields.Float(string="Combustible necesario ruta 1", compute="_com_com_necesario1")
    combustible2 = fields.Float(string="Combustible necesario ruta 2", compute="_com_com_necesario2")
    viaje_gm = fields.Char(string="Viaje GM")
    modalidad_ruta1 = fields.Selection([('vacio','Vacio'),('medido','Medido'),('pesado','Pesado')],string="Modalidad de ruta 1",default='medido')
    modalidad_ruta2 = fields.Selection([('vacio','Vacio'),('medido','Medido'),('pesado','Pesado')],string="Modalidad de ruta 2",default='medido')
    rendimiento_manual1= fields.Boolean(string="Rendimiento Manual Ruta 1?")
    rendimiento_manual2= fields.Boolean(string="Rendimiento Manual Ruta 2?")
    kmlmuno = fields.Float(string="KM/L")
    kmlm2 = fields.Float(string="KM/L")
    presupuesto_creado= fields.Boolean(string="Presupuesto creado?", default=False, compute="_com_pres_creado")

    @api.one
    def _com_pres_creado(self):
        if self.subpedido_id:
            self.presupuesto_creado = True
        if not self.subpedido_id:
            self.presupuesto_creado = False

    @api.depends('unit_id')
    @api.one
    def _comp_fuel_kml(self):
        self.kml = self.unit_id.efficiency

    # @api.one
    # def _com_com_necesario(self):
    #     if self.route2_id:
    #         if self.rendimiento_manual1 == True and self.rendimiento_manual2 != True:
    #             if self.kmlmuno > 0 and self.kml <= 0:
    #                 self.com_necesario = (self.route_id.distance/self.kmlmuno)
    #             if self.kmlmuno <= 0 and self.kml > 0:
    #                 self.com_necesario = (self.route2_id.distance/self.kml)
    #             if self.kmlmuno > 0 and self.kml > 0:
    #                 self.com_necesario = (self.route_id.distance/self.kmlmuno) + (self.route2_id.distance/self.kml)
    #         if self.rendimiento_manual1 != True and self.rendimiento_manual2 == True:
    #             if self.kml > 0 and self.kmlm2 <= 0:
    #                 self.com_necesario = (self.route_id.distance/self.kml)
    #             if self.kml <= 0 and self.kmlm2 > 0:
    #                 self.com_necesario = (self.route2_id.distance/self.kmlm2)
    #             if self.kml > 0 and self.kmlm2 > 0:
    #                 self.com_necesario = (self.route_id.distance/self.kml) + (self.route2_id.distance/self.kmlm2)
    #         if self.rendimiento_manual1 == True and self.rendimiento_manual2 == True:
    #             if self.kmlmuno > 0 and self.kmlm2 <= 0:
    #                 self.com_necesario = (self.route_id.distance/self.kmlmuno)
    #             if self.kmlmuno <= 0 and self.kmlm2 > 0:
    #                 self.com_necesario = (self.route2_id.distance/self.kmlm2)
    #             if self.kmlmuno > 0 and self.kmlm2 > 0:
    #                 self.com_necesario = (self.route_id.distance/self.kmlmuno) + (self.route2_id.distance/self.kmlm2)
    #         if self.rendimiento_manual1 != True and self.rendimiento_manual2 != True:
    #             if self.kml > 0:
    #                 self.com_necesario = (self.route_id.distance/self.kml) + (self.route2_id.distance/self.kml)
    #     else:
    #         if self.rendimiento_manual1 == True:
    #             if self.kmlmuno > 0:
    #                 self.com_necesario = self.route_id.distance/self.kmlmuno
    #         if self.rendimiento_manual1 != True:
    #             if self.kml > 0:
    #                 self.com_necesario = self.route_id.distance/self.kml

    @api.one
    def _com_com_necesario1(self):
        if self.route_id:
            if self.rendimiento_manual1 == True:
                if self.kmlmuno > 0:
                    if self.kml_ex == True:
                        self.update({'combustible1':(self.route_id.distance+self.kmlextra)/self.kmlmuno})
                    if self.kml_ex != True:
                        self.update({'combustible1':self.route_id.distance/self.kmlmuno})
                   


            if self.rendimiento_manual1 != True:
                if self.kml > 0:
                    if self.kml_ex == True:
                        self.update({'combustible1':(self.route_id.distance+self.kmlextra)/self.kml})
                    if self.kml_ex != True:
                        self.update({'combustible1':self.route_id.distance/self.kml})

    @api.one
    def _com_com_necesario2(self):
        if self.route2_id:
            if self.rendimiento_manual2 == True:
                if self.kmlm2 > 0:
                    if self.kml_ex2 == True:
                        self.update({'combustible2':(self.route2_id.distance+self.kmlextra2)/self.kmlm2})
                    if self.kml_ex2 != True:
                        self.update({'combustible2':self.route2_id.distance/self.kmlm2})
                   

            if self.rendimiento_manual2 != True:
                if self.kml > 0:
                    if self.kml_ex2 == True:
                        self.update({'combustible2':(self.route2_id.distance+self.kmlextra2)/self.kml})
                    if self.kml_ex2 != True:   
                        self.update({'combustible2':self.route2_id.distance/self.kml})

    @api.onchange('route_id','rendimiento_manual1','kml','kmlmuno','kmlextra','kml_ex')
    def _onchange_necesario1(self):
        if self.route_id:
            if self.rendimiento_manual1 == True:
                if self.kmlmuno > 0:
                    if self.kml_ex == True:
                        self.update({'combustible1':(self.route_id.distance+self.kmlextra)/self.kmlmuno})
                    if self.kml_ex != True:
                        self.update({'combustible1':self.route_id.distance/self.kmlmuno})
                       
            if self.rendimiento_manual1 != True:
                if self.kml > 0:
                    if self.kml_ex == True:
                        self.update({'combustible1':(self.route_id.distance+self.kmlextra)/self.kml})
                    if self.kml_ex != True:
                        self.update({'combustible1':self.route_id.distance/self.kml})


    @api.onchange('route2_id','rendimiento_manual2','kml','kmlm2','kmlextra2','kml_ex2')
    def _onchenge_necesario2(self):
        if self.route2_id:
            if self.rendimiento_manual2 == True:
                if self.kmlm2 > 0:
                    if self.kml_ex2 == True:
                        self.update({'combustible2':(self.route2_id.distance+self.kmlextra2)/self.kmlm2})
                    if self.kml_ex2 != True:
                        self.update({'combustible2':self.route2_id.distance/self.kmlm2})
            if self.rendimiento_manual2 != True:
                if self.kml > 0:
                    if self.kml_ex2 == True:
                        self.update({'combustible2':(self.route2_id.distance+self.kmlextra2)/self.kml})
                    if self.kml_ex2 != True:
                        self.update({'combustible2':self.route2_id.distance/self.kml})

    @api.onchange('route_id','route2_id','rendimiento_manual1','rendimiento_manual2','kml','kmlmuno','kmlm2','kmlextra','kmlextra2','kml_ex','kml_ex2')
    def _onchange_com_necesario(self):
        if self.kmlextra > 0 or self.kmlextra2 > 0:
            if self.route2_id:
                if self.rendimiento_manual1 == True and self.rendimiento_manual2 != True:
                    if self.kmlmuno > 0 and self.kml <= 0:
                        self.com_necesario = ((self.route_id.distance+self.kmlextra)/self.kmlmuno)
                    if self.kmlmuno <= 0 and self.kml > 0:
                        self.com_necesario = ((self.route2_id.distance+self.kmlextra2)/self.kml)
                    if self.kmlmuno > 0 and self.kml > 0:
                        self.com_necesario = ((self.route_id.distance+self.kmlextra)/self.kmlmuno) + ((self.route2_id.distance+self.kmlextra2)/self.kml)
                if self.rendimiento_manual1 != True and self.rendimiento_manual2 == True:
                    if self.kml > 0 and self.kmlm2 <= 0:
                        self.com_necesario = ((self.route_id.distance+self.kmlextra)/self.kml)
                    if self.kml <= 0 and self.kmlm2 > 0:
                        self.com_necesario = ((self.route2_id.distance+self.kmlextra2)/self.kmlm2)
                    if self.kml > 0 and self.kmlm2 > 0:
                        self.com_necesario = ((self.route_id.distance+self.kmlextra)/self.kml) + ((self.route2_id.distance+self.kmlextra2)/self.kmlm2)
                if self.rendimiento_manual1 == True and self.rendimiento_manual2 == True:
                    if self.kmlmuno > 0 and self.kmlm2 <= 0:
                        self.com_necesario = ((self.route_id.distance+self.kmlextra)/self.kmlmuno)
                    if self.kmlmuno <= 0 and self.kmlm2 > 0:
                        self.com_necesario = ((self.route2_id.distance+self.kmlextra2)/self.kmlm2)
                    if self.kmlmuno > 0 and self.kmlm2 > 0:
                        self.com_necesario = ((self.route_id.distance+self.kmlextra)/self.kmlmuno) + ((self.route2_id.distance+self.kmlextra2)/self.kmlm2)
                if self.rendimiento_manual1 != True and self.rendimiento_manual2 != True:
                    if self.kml > 0:
                        self.com_necesario = ((self.route_id.distance+self.kmlextra)/self.kml) + ((self.route2_id.distance+self.kmlextra2)/self.kml)
            else:
                if self.rendimiento_manual1 == True:
                    if self.kmlmuno > 0:
                        self.com_necesario = (self.route_id.distance+self.kmlextra)/self.kmlmuno
                if self.rendimiento_manual1 != True:
                    if self.kml > 0:
                        self.com_necesario = (self.route_id.distance+self.kmlextra)/self.kml
        else:
            if self.route2_id:
                if self.rendimiento_manual1 == True and self.rendimiento_manual2 != True:
                    if self.kmlmuno > 0 and self.kml <= 0:
                        self.com_necesario = (self.route_id.distance/self.kmlmuno)
                    if self.kmlmuno <= 0 and self.kml > 0:
                        self.com_necesario = (self.route2_id.distance/self.kml)
                    if self.kmlmuno > 0 and self.kml > 0:
                        self.com_necesario = (self.route_id.distance/self.kmlmuno) + (self.route2_id.distance/self.kml)
                if self.rendimiento_manual1 != True and self.rendimiento_manual2 == True:
                    if self.kml > 0 and self.kmlm2 <= 0:
                        self.com_necesario = (self.route_id.distance/self.kml)
                    if self.kml <= 0 and self.kmlm2 > 0:
                        self.com_necesario = (self.route2_id.distance/self.kmlm2)
                    if self.kml > 0 and self.kmlm2 > 0:
                        self.com_necesario = (self.route_id.distance/self.kml) + (self.route2_id.distance/self.kmlm2)
                if self.rendimiento_manual1 == True and self.rendimiento_manual2 == True:
                    if self.kmlmuno > 0 and self.kmlm2 <= 0:
                        self.com_necesario = (self.route_id.distance/self.kmlmuno)
                    if self.kmlmuno <= 0 and self.kmlm2 > 0:
                        self.com_necesario = (self.route2_id.distance/self.kmlm2)
                    if self.kmlmuno > 0 and self.kmlm2 > 0:
                        self.com_necesario = (self.route_id.distance/self.kmlmuno) + (self.route2_id.distance/self.kmlm2)
                if self.rendimiento_manual1 != True and self.rendimiento_manual2 != True:
                    if self.kml > 0:
                        self.com_necesario = (self.route_id.distance/self.kml) + (self.route2_id.distance/self.kml)
            else:
                if self.rendimiento_manual1 == True:
                    if self.kmlmuno > 0:
                        self.com_necesario = self.route_id.distance/self.kmlmuno
                if self.rendimiento_manual1 != True:
                    if self.kml > 0:
                        self.com_necesario = self.route_id.distance/self.kml

    @api.onchange('route_id','route2_id')
    def _onchange_routes(self):
        line_ids = []
        res = {'value':{
                'cargo_id':[],
            }
        }
        for x in self.route_id.cargos_id:
            line = {
              'name': x.name.id,
              'valor': x.valor,
              'sistema': x.sistema,
            }
            line_ids += [line]
        for x in self.route2_id.cargos_id:
            line = {
              'name': x.name.id,
              'valor': x.valor,
              'sistema': x.sistema,
            }
            line_ids += [line]
        res['value'].update({
            'cargo_id': line_ids,
        })
        return res

    @api.onchange('route_id','route2_id','rendimiento_manual1','rendimiento_manual2','kml','kmlmuno','kmlm2','operating_unit_id','unit_id','employee_id','com_necesario','kmlextra','kmlextra2')
    def _onchange_route_unit(self):
        vale = 0
        if self.kmlextra > 0 or self.kmlextra2 > 0:
            if self.route2_id:
                if self.rendimiento_manual1 == True and self.rendimiento_manual2 != True:
                    if self.kmlmuno > 0 and self.kml <= 0:
                        vale = ((self.route_id.distance+self.kmlextra)/self.kmlmuno)
                    if self.kmlmuno <= 0 and self.kml > 0:
                        vale = ((self.route2_id.distance+self.kmlextra2)/self.kml)
                    if self.kmlmuno > 0 and self.kml > 0:
                        vale = ((self.route_id.distance+self.kmlextra)/self.kmlmuno) + ((self.route2_id.distance+self.kmlextra2)/self.kml)
                if self.rendimiento_manual1 != True and self.rendimiento_manual2 == True:
                    if self.kml > 0 and self.kmlm2 <= 0:
                        vale = ((self.route_id.distance+self.kmlextra)/self.kml)
                    if self.kml <= 0 and self.kmlm2 > 0:
                        vale = ((self.route2_id.distance+self.kmlextra2)/self.kmlm2)
                    if self.kml > 0 and self.kmlm2 > 0:
                        vale = ((self.route_id.distance+self.kmlextra)/self.kml) + ((self.route2_id.distance+self.kmlextra2)/self.kmlm2)
                if self.rendimiento_manual1 == True and self.rendimiento_manual2 == True:
                    if self.kmlmuno > 0 and self.kmlm2 <= 0:
                        vale = ((self.route_id.distance+self.kmlextra)/self.kmlmuno)
                    if self.kmlmuno <= 0 and self.kmlm2 > 0:
                        vale = ((self.route2_id.distance+self.kmlextra2)/self.kmlm2)
                    if self.kmlmuno > 0 and self.kmlm2 > 0:
                        vale = ((self.route_id.distance+self.kmlextra)/self.kmlmuno) + ((self.route2_id.distance+self.kmlextra2)/self.kmlm2)
                if self.rendimiento_manual1 != True and self.rendimiento_manual2 != True:
                    if self.kml > 0:
                        vale = ((self.route_id.distance+self.kmlextra)/self.kml) + ((self.route2_id.distance+self.kmlextra2)/self.kml)
            else:
                if self.rendimiento_manual1 == True:
                    if self.kmlmuno > 0:
                        vale = (self.route_id.distance+self.kmlextra)/self.kmlmuno
                if self.rendimiento_manual1 != True:
                    if self.kml > 0:
                        vale = (self.route_id.distance+self.kmlextra)/self.kml
        else:
            if self.route2_id:
                if self.rendimiento_manual1 == True and self.rendimiento_manual2 != True:
                    if self.kmlmuno > 0 and self.kml <= 0:
                        vale = (self.route_id.distance/self.kmlmuno)
                    if self.kmlmuno <= 0 and self.kml > 0:
                        vale = (self.route2_id.distance/self.kml)
                    if self.kmlmuno > 0 and self.kml > 0:
                        vale = (self.route_id.distance/self.kmlmuno) + (self.route2_id.distance/self.kml)
                if self.rendimiento_manual1 != True and self.rendimiento_manual2 == True:
                    if self.kml > 0 and self.kmlm2 <= 0:
                        vale = (self.route_id.distance/self.kml)
                    if self.kml <= 0 and self.kmlm2 > 0:
                        vale = (self.route2_id.distance/self.kmlm2)
                    if self.kml > 0 and self.kmlm2 > 0:
                        vale = (self.route_id.distance/self.kml) + (self.route2_id.distance/self.kmlm2)
                if self.rendimiento_manual1 == True and self.rendimiento_manual2 == True:
                    if self.kmlmuno > 0 and self.kmlm2 <= 0:
                        vale = (self.route_id.distance/self.kmlmuno)
                    if self.kmlmuno <= 0 and self.kmlm2 > 0:
                        vale = (self.route2_id.distance/self.kmlm2)
                    if self.kmlmuno > 0 and self.kmlm2 > 0:
                        vale = (self.route_id.distance/self.kmlmuno) + (self.route2_id.distance/self.kmlm2)
                if self.rendimiento_manual1 != True and self.rendimiento_manual2 != True:
                    if self.kml > 0:
                        vale = (self.route_id.distance/self.kml) + (self.route2_id.distance/self.kml)
            else:
                if self.rendimiento_manual1 == True:
                    if self.kmlmuno > 0:
                        vale = self.route_id.distance/self.kmlmuno
                if self.rendimiento_manual1 != True:
                    if self.kml > 0:
                        vale = self.route_id.distance/self.kml
		"""
        line_ids = []
        res = {'value':{
                'fuel_log_ids':[],
            }
        }
        comb = self.env['product.product'].search([('tms_product_category','=','fuel'),('es_combustible','=',True)], limit=1)
        line = {
          'operating_unit_id': self.operating_unit_id.id,
          'vendor_id': self.operating_unit_id.default_provider_fuel.id,
          'vehicle_id': self.unit_id.id,
          'product_id': comb.id,
          'product_qty': vale,
          'employee_id': self.employee_id.id,
          'currency_id': self.env.user.company_id.currency_id.id,
          'state':'draft'
        }
        line_ids += [line]
        res['value'].update({
            'fuel_log_ids': line_ids,
        })
        return res
		"""
		
		#----------------------------------------------------
       
        if len(self.fuel_log_ids) > 0: #Actualizar existente.
            lista = []
            for x in self.fuel_log_ids:
                if x.sistema:
                    comb = self.env['product.product'].search([('tms_product_category', '=', 'fuel'), ('es_combustible', '=', True)], limit=1)
                    valores = {
                    'operating_unit_id': x.operating_unit_id,
                    'vendor_id': x.vendor_id,
                    'vehicle_id': x.vehicle_id,
                    'product_id': x.product_id,
                    'product_qty': vale,
                    'price_total': 0,
                    'employee_id': x.employee_id,
                    'currency_id': x.currency_id,
                    'state': x.state
                    }
                    x.update(valores)
        elif self.unit_id:  #Agregar nuevo.
            total = 0
            comb = self.env['product.product'].search([('tms_product_category', '=', 'fuel'), ('es_combustible', '=', True)], limit=1)
            
            valores = {
              'operating_unit_id': self.operating_unit_id.id,
              'vendor_id': self.operating_unit_id.default_provider_fuel.id,
              'vehicle_id': self.unit_id.id,
              'product_id': comb.id,
              'product_qty': vale,
              'price_total': 0,
              'employee_id': self.employee_id.id,
              'currency_id': self.env.user.company_id.currency_id.id,
              'state': 'draft',
              'sistema': True
            }
            self.update({'fuel_log_ids': [(0, 0, valores)]})
        
        #Calculos.
        for x in self.fuel_log_ids:
            if x.sistema:
                tax = 0
                for t in x.product_id.supplier_taxes_id:
                    tax += t.amount
                x.tax_amount = x.product_qty * (x.product_id.standard_price * (tax / 100))
                x.price_unit = x.product_id.standard_price
                x.price_subtotal = x.price_unit * x.product_qty
                x.price_total = x.tax_amount + x.price_subtotal



    si_seguro = fields.Boolean(string="Seguro de carga.", default=False)
    condiciones_seguro = fields.Text(string="Condiciones del seguro.")
    cargo_seguro = fields.Float(string="Cargo del seguro")

    lavado = fields.Boolean(string="Lavado de camión", default=False)
    cargo_lavado = fields.Float(string="Cargo de lavado")

    plastico = fields.Boolean(string="Plastico del camión", default=False)
    cargo_plastico = fields.Float(string="Cargo por plastico")

    fumigado = fields.Boolean(string="Fumigado", default=False)
    cargo_fumigado = fields.Float(string="Cargo por fumigado")

    otros = fields.Boolean(string="Otros", default=False)
    cargo_otros = fields.Float(string="Cargo por otros servicios")
    des_otros = fields.Text(string="Especificaiones")

    camisa = fields.Boolean(string="Camisa",default=False)
    camisa_manga = fields.Selection([('corta','Manga Corta'),('larga','Manga Larga')], string="Manga")
    camisa_mat = fields.Char(string="Material Especial")
    cargo_camisa = fields.Float(string="Cargo por ")

    chaleco = fields.Boolean(string="Chaleco",default=False)
    chaleco_color = fields.Char(string="Color")
    cargo_chaleco = fields.Float(string="Cargo por chaleco")

    guantes = fields.Boolean(string="Guantes",default=False)
    tipo_guantes = fields.Char(string="Tipo de guantes")
    cargo_guantes = fields.Float(string="Cargo por guantes")
    
    pantalon = fields.Boolean(string="Pantalon",default=False)
    pantalon_sua = fields.Char(string="SUA")
    pantalon_mat = fields.Char(string="Material de pantalon")
    cargo_pantalon = fields.Float(string="Cargo por pantalon")

    @api.multi
    def create_sale_order(self):
        so=self.env['sale.order'].create({
            'name': self.env['ir.sequence'].next_by_code('sale.order') or _('New'),
            'partner_id':self.cliente_id.id,
            'tarifa_cliente':self.tarifa_cliente,
            'product': self.producto.id,
            'ruta':self.route_id.id,
            'ruta2':self.route2_id.id,
            'date_order':fields.datetime.now(),
            'origin':self.name,
            })
        self.subpedido_id = so.id
    

        # product_caseta_obj = self.env['product.product'].search([('es_caseta','=',True)], limit=1)
        # self.env['sale.order.line'].create({
        #   'product_id': product_caseta_obj.id,
        #   'product_uom': product_caseta_obj.uom_id.id,
        #   'name': 'Costo de casetas generado del viaje',
        #   'price_unit': self.costo_casetas,
        #   'product_uom_qty':1,
        #   'order_id': so.id
        #   })

        product_felte_obj = self.env['product.product'].search([('es_flete','=',True)], limit=1)
        # fuel = 0
        # for x in self.fuel_log_ids:
        #     fuel += x.price_total
        self.env['sale.order.line'].create({
          'product_id': product_felte_obj.id,
          'product_uom': product_felte_obj.uom_id.id,
          'name': 'Costos del flete del viaje',
          'price_unit': self.flete_cliente,
          'product_uom_qty':1,
          'order_id': so.id
          })
        if self.cargo_id:
            cargos = 0
            for x in self.cargo_id:
                cargos += x.valor
            product_cargo_obj = self.env['product.product'].search([('es_cargo','=',True)], limit=1)
            self.env['sale.order.line'].create({
              'product_id': product_cargo_obj.id,
              'product_uom': product_cargo_obj.uom_id.id,
              'name': 'Cargos extra del viaje',
              'price_unit': cargos,
              'product_uom_qty':1,
              'order_id': so.id
              })

        #DMC
        if self.si_seguro:
            product_dmc_seguro = self.env['product.product'].search([('dmc_seguro','=',True)], limit=1)
            print("Producto seguro: " + str(product_dmc_seguro.name))
            self.env['sale.order.line'].create({
              'product_id': product_dmc_seguro.id,
              'product_uom': product_dmc_seguro.uom_id.id,
              'name': 'Cargo por Seguro',
              'price_unit': self.cargo_seguro,
              'product_uom_qty':1,
              'order_id': so.id
              })
        if self.lavado:
            product_dmc_lavado = self.env['product.product'].search([('dmc_lavado','=',True)], limit=1)
            self.env['sale.order.line'].create({
              'product_id': product_dmc_lavado.id,
              'product_uom': product_dmc_lavado.uom_id.id,
              'name': 'Cargo por Lavado',
              'price_unit': self.cargo_lavado,
              'product_uom_qty':1,
              'order_id': so.id
              })
        if self.plastico:
            product_dmc_plastico = self.env['product.product'].search([('dmc_plastico','=',True)], limit=1)
            self.env['sale.order.line'].create({
              'product_id': product_dmc_plastico.id,
              'product_uom': product_dmc_plastico.uom_id.id,
              'name': 'Cargo por Plastico',
              'price_unit': self.cargo_plastico,
              'product_uom_qty':1,
              'order_id': so.id
              })
        if self.fumigado:
            product_dmc_fumigado = self.env['product.product'].search([('dmc_fumigado','=',True)], limit=1)
            self.env['sale.order.line'].create({
              'product_id': product_dmc_fumigado.id,
              'product_uom': product_dmc_fumigado.uom_id.id,
              'name': 'Cargo por Fumigado',
              'price_unit': self.cargo_fumigado,
              'product_uom_qty':1,
              'order_id': so.id
              })
        if self.otros:
            product_dmc_otros = self.env['product.product'].search([('dmc_otros','=',True)], limit=1)
            self.env['sale.order.line'].create({
              'product_id': product_dmc_otros.id,
              'product_uom': product_dmc_otros.uom_id.id,
              'name': 'Cargo por Otros',
              'price_unit': self.cargo_otros,
              'product_uom_qty':1,
              'order_id': so.id
              })
        if self.camisa:
            product_dmc_camisa = self.env['product.product'].search([('dmc_camisa','=',True)], limit=1)
            self.env['sale.order.line'].create({
              'product_id': product_dmc_camisa.id,
              'product_uom': product_dmc_camisa.uom_id.id,
              'name': 'Cargo por Camisa Operador',
              'price_unit': self.cargo_camisa,
              'product_uom_qty':1,
              'order_id': so.id
              })
        if self.chaleco:
            product_dmc_chaleco = self.env['product.product'].search([('dmc_chaleco','=',True)], limit=1)
            self.env['sale.order.line'].create({
              'product_id': product_dmc_chaleco.id,
              'product_uom': product_dmc_chaleco.uom_id.id,
              'name': 'Cargo por Chaleco Operador',
              'price_unit': self.cargo_chaleco,
              'product_uom_qty':1,
              'order_id': so.id
              })
        if self.pantalon:
            product_dmc_pantalon = self.env['product.product'].search([('dmc_pantalon','=',True)], limit=1)
            self.env['sale.order.line'].create({
              'product_id': product_dmc_pantalon.id,
              'product_uom': product_dmc_pantalon.uom_id.id,
              'name': 'Cargo por Pantalon Operador',
              'price_unit': self.cargo_pantalon,
              'product_uom_qty':1,
              'order_id': so.id
              })
        if self.guantes:
            product_dmc_guantes = self.env['product.product'].search([('dmc_guantes','=',True)], limit=1)
            self.env['sale.order.line'].create({
              'product_id': product_dmc_guantes.id,
              'product_uom': product_dmc_guantes.uom_id.id,
              'name': 'Cargo por Guantes Operador',
              'price_unit': self.cargo_guantes,
              'product_uom_qty':1,
              'order_id': so.id
              })

    crear_ope=fields.Boolean(string="crear nuevo registro")
    @api.multi
    def create_nuevo_operador(self):
        travel= self.env['tms.travel'].search([('name','=',self.name)], limit=1)
        ids=travel.id
        new_op=self.env['tms.travel'].create({
            'travels_id':ids,
            'facturar':True,
            'cliente_id':self.cliente_id.id,
            'producto':self.producto.id,
            'costo_producto': self.costo_producto,
            'sucursal_id':self.sucursal_id.id,
            'lineanegocio':self.lineanegocio.id,
            'date':fields.datetime.now(),
            'tipo_remolque':self.tipo_remolque,
            'tipo_carga':self.tipo_carga.id,
            'unit_id':self.unit_id.id,
            'route_id':self.route_id.id,
            'crear_ope':True,
            })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'tms.travel',
            'view_mode': 'form',
            'res_id': new_op.id,
            'target': 'current',
            'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
            }

    @api.onchange('driver_factor_ids','route_id','route2_id','tipo_carga','modalidad_ruta1','modalidad_ruta2','tarifa_cliente','tarifa_cliente2','kmlextra','kmlextra2')
    def _onchange_type_factor(self):
        for x in self.driver_factor_ids:
            if x.factor_type == 'costokm':
                if self.tipo_remolque == 'sencillo':
                    if self.modalidad_ruta1 == 'vacio':
                        x.valor = self.tipo_carga.tarifa_sencillo_vacio
                    if self.modalidad_ruta1 == 'medido':
                        x.valor = self.tipo_carga.tarifa_sencillo_medido
                    if self.modalidad_ruta1 == 'pesado':
                        x.valor = self.tipo_carga.tarifa_sencillo_pesado
                    if self.modalidad_ruta2 == 'vacio':
                        x.valor2 = self.tipo_carga.tarifa_sencillo_vacio
                    if self.modalidad_ruta2 == 'medido':
                        x.valor2 = self.tipo_carga.tarifa_sencillo_medido
                    if self.modalidad_ruta2 == 'pesado':
                        x.valor2 = self.tipo_carga.tarifa_sencillo_pesado
                if self.tipo_remolque == 'doble':
                    if self.modalidad_ruta1 == 'vacio':
                        x.valor = self.tipo_carga.tarifa_doble_vacio
                    if self.modalidad_ruta1 == 'medido':
                        x.valor = self.tipo_carga.tarifa_doble_medido
                    if self.modalidad_ruta1 == 'pesado':
                        x.valor = self.tipo_carga.tarifa_doble_pesado
                    if self.modalidad_ruta2 == 'vacio':
                        x.valor2 = self.tipo_carga.tarifa_doble_vacio
                    if self.modalidad_ruta2 == 'medido':
                        x.valor2 = self.tipo_carga.tarifa_doble_medido
                    if self.modalidad_ruta2 == 'pesado':
                        x.valor2 = self.tipo_carga.tarifa_doble_pesado
                if self.tipo_remolque == 'torton':
                    if self.modalidad_ruta1 == 'vacio':
                        x.valor = self.tipo_carga.tarifa_torton_vacio
                    if self.modalidad_ruta1 == 'medido':
                        x.valor = self.tipo_carga.tarifa_torton_medido
                    if self.modalidad_ruta1 == 'pesado':
                        x.valor = self.tipo_carga.tarifa_torton_pesado
                    if self.modalidad_ruta2 == 'vacio':
                        x.valor2 = self.tipo_carga.tarifa_torton_vacio
                    if self.modalidad_ruta2 == 'medido':
                        x.valor2 = self.tipo_carga.tarifa_torton_medido
                    if self.modalidad_ruta2 == 'pesado':
                        x.valor2 = self.tipo_carga.tarifa_torton_pesado
                if self.tipo_remolque == 'rabon':
                    if self.modalidad_ruta1 == 'vacio':
                        x.valor = self.tipo_carga.tarifa_rabon_vacio
                    if self.modalidad_ruta1 == 'medido':
                        x.valor = self.tipo_carga.tarifa_rabon_medido
                    if self.modalidad_ruta1 == 'pesado':
                        x.valor = self.tipo_carga.tarifa_rabon_pesado
                    if self.modalidad_ruta2 == 'vacio':
                        x.valor2 = self.tipo_carga.tarifa_rabon_vacio
                    if self.modalidad_ruta2 == 'medido':
                        x.valor2 = self.tipo_carga.tarifa_sencillo_medido
                    if self.modalidad_ruta2 == 'pesado':
                        x.valor2 = self.tipo_carga.tarifa_sencillo_pesado
                if x.if_diferentes != True:
                    x.valor2 = x.valor
            if x.factor_type != 'costokm':
                x.if_diferentes == False

    @api.onchange('driver_factor_ids','route_id','route2_id','tipo_carga','modalidad_ruta1','modalidad_ruta2','tarifa_cliente','tarifa_cliente2','flete_cliente','kmlextra','kmlextra2')
    def _onchange_cal_total_factor(self):
        for x in self.driver_factor_ids:
            if x.factor_type == 'costo_fijo':
                x.total = x.valor
            if x.factor_type == 'porcentaje':
                x.total = (self.flete_cliente/100) * x.valor
            if x.factor_type == 'costokm':

                if self.kmlextra > 0 or self.kmlextra2 > 0:
                    if x.if_diferentes != True:
                        x.total = x.valor * ((self.route_id.distance+self.kmlextra) + (self.route2_id.distance+self.kmlextra2))
                    if x.if_diferentes == True:
                        x.total = (x.valor * (self.route_id.distance+self.kmlextra)) + (x.valor2 * (self.route2_id.distance+self.kmlextra2))
                else:
                    if x.if_diferentes != True:
                        x.total = x.valor * (self.route_id.distance + self.route2_id.distance)
                    if x.if_diferentes == True:
                        x.total = (x.valor * self.route_id.distance) + (x.valor2 * self.route2_id.distance)

    com_solicitado = fields.Float()

    @api.onchange('fuel_log_ids','route_id','route2_id')
    def _onchange_com_soli(self):
        tot_comb = 0
        for l in self.fuel_log_ids:
            tot_comb += l.product_qty
        self.com_solicitado = tot_comb


    @api.one
    def _compute_com_soli(self):
        tot_comb = 0
        for l in self.fuel_log_ids:
            tot_comb += l.product_qty
        self.com_solicitado = tot_comb

    #checar
    @api.multi
    def write(self, vals):
        necesario = 0
        res = super(TmsTravel, self).write(vals)
        if self.kmlextra > 0 or self.kmlextra2 > 0:
            if self.route2_id:
                if self.rendimiento_manual1 == True and self.rendimiento_manual2 != True:
                    if self.kmlmuno > 0 and self.kml <= 0:
                        necesario = ((self.route_id.distance+self.kmlextra)/self.kmlmuno)
                    if self.kmlmuno <= 0 and self.kml > 0:
                        necesario = ((self.route2_id.distance+self.kmlextra2)/self.kml)
                    if self.kmlmuno > 0 and self.kml > 0:
                        necesario = ((self.route_id.distance+self.kmlextra)/self.kmlmuno) + ((self.route2_id.distance+self.kmlextra2)/self.kml)
                if self.rendimiento_manual1 != True and self.rendimiento_manual2 == True:
                    if self.kml > 0 and self.kmlm2 <= 0:
                        necesario = ((self.route_id.distance+self.kmlextra)/self.kml)
                    if self.kml <= 0 and self.kmlm2 > 0:
                        necesario = ((self.route2_id.distance+self.kmlextra2)/self.kmlm2)
                    if self.kml > 0 and self.kmlm2 > 0:
                        necesario = ((self.route_id.distance+self.kmlextra)/self.kml) + ((self.route2_id.distance+self.kmlextra2)/self.kmlm2)
                if self.rendimiento_manual1 == True and self.rendimiento_manual2 == True:
                    if self.kmlmuno > 0 and self.kmlm2 <= 0:
                        necesario = ((self.route_id.distance+self.kmlextra)/self.kmlmuno)
                    if self.kmlmuno <= 0 and self.kmlm2 > 0:
                        necesario = ((self.route2_id.distance+self.kmlextra2)/self.kmlm2)
                    if self.kmlmuno > 0 and self.kmlm2 > 0:
                        necesario = ((self.route_id.distance+self.kmlextra)/self.kmlmuno) + ((self.route2_id.distance+self.kmlextra2)/self.kmlm2)
                if self.rendimiento_manual1 != True and self.rendimiento_manual2 != True:
                    if self.kml > 0:
                        necesario = ((self.route_id.distance++self.kmlextra)/self.kml) + ((self.route2_id.distance+self.kmlextra2)/self.kml)
            else:
                if self.rendimiento_manual1 == True:
                    if self.kmlmuno > 0:
                        necesario = (self.route_id.distance+self.kmlextra)/self.kmlmuno
                if self.rendimiento_manual1 != True:
                    if self.kml > 0:
                        necesario = (self.route_id.distance+self.kmlextra)/self.kml
        else:
            if self.route2_id:
                if self.rendimiento_manual1 == True and self.rendimiento_manual2 != True:
                    if self.kmlmuno > 0 and self.kml <= 0:
                        necesario = (self.route_id.distance/self.kmlmuno)
                    if self.kmlmuno <= 0 and self.kml > 0:
                        necesario = (self.route2_id.distance/self.kml)
                    if self.kmlmuno > 0 and self.kml > 0:
                        necesario = (self.route_id.distance/self.kmlmuno) + (self.route2_id.distance/self.kml)
                if self.rendimiento_manual1 != True and self.rendimiento_manual2 == True:
                    if self.kml > 0 and self.kmlm2 <= 0:
                        necesario = (self.route_id.distance/self.kml)
                    if self.kml <= 0 and self.kmlm2 > 0:
                        necesario = (self.route2_id.distance/self.kmlm2)
                    if self.kml > 0 and self.kmlm2 > 0:
                        necesario = (self.route_id.distance/self.kml) + (self.route2_id.distance/self.kmlm2)
                if self.rendimiento_manual1 == True and self.rendimiento_manual2 == True:
                    if self.kmlmuno > 0 and self.kmlm2 <= 0:
                        necesario = (self.route_id.distance/self.kmlmuno)
                    if self.kmlmuno <= 0 and self.kmlm2 > 0:
                        necesario = (self.route2_id.distance/self.kmlm2)
                    if self.kmlmuno > 0 and self.kmlm2 > 0:
                        necesario = (self.route_id.distance/self.kmlmuno) + (self.route2_id.distance/self.kmlm2)
                if self.rendimiento_manual1 != True and self.rendimiento_manual2 != True:
                    if self.kml > 0:
                        necesario = (self.route_id.distance/self.kml) + (self.route2_id.distance/self.kml)
            else:
                if self.rendimiento_manual1 == True:
                    if self.kmlmuno > 0:
                        necesario = self.route_id.distance/self.kmlmuno
                if self.rendimiento_manual1 != True:
                    if self.kml > 0:
                        necesario = self.route_id.distance/self.kml
        print(vals.get('com_solicitado'))
        print(round(necesario, 2))
        if vals.get('com_solicitado') > round(necesario, 2):
            raise UserError(
                _('Aviso !\nLa suma en los vales de combustible ('+'{0:.2f}'.format(vals.get('com_solicitado'))+' Litros) es mayor al necesario. (' + str(round(necesario, 2)) + ' Litros)'))
        return res

    @api.model
    def _get_com_necesario(self, vals):
        return vals.get('com_necesario')


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

    # @api.model
    # def _advance_ids(self, vals):
    #     t_id = vals.get['line_cargo_id']
    #     if t_id:
    #         travel = self.env['tms.travel'].search([('id','=',t_id)])
    #         ids = []
    #         for x in self.line_cargo_id.advance_ids:
    #             ids.append(x.id)
    #         print(ids)
    #         return [('id', 'in', ids)]
    #     else:
    #         return []

    name = fields.Many2one('tms.tipocargosadicionales', string='Tipos de cargos adicionales', required=True)
    valor = fields.Float(string='Valor', required=True)
    line_cargo_id = fields.Many2one('tms.travel', string='Id viaje')
    sistema = fields.Boolean(string="Sistema", default=False)  # Indica si es un registro del sistema.
    route_id = fields.Many2one("tms.route", string="Ruta")
    adjunto_compro = fields.Binary(string="Comprobante")
    filename = fields.Char('file name')
    advance_id = fields.Many2one("tms.advance", string="Anticipo")

    state = fields.Selection([('pendiente','Pendiente'),('aprobado','Aprobado'),('rechazado','Rechazado')], string="Estado", default="pendiente")
    # @api.constrains('name')
    # def _check_name(self):
    #     obj = self.env['tms.viaje.cargos'].search(
    #         [('name', '=', self.name.id), ('line_cargo_id', '=', self.line_cargo_id.id)])
    #     if len(obj) > 1:
    #         raise UserError(
    #             _('Aviso !\nNo se puede crear cargos del mismo tipo mas de 1 vez.'))
    @api.multi
    def action_cancel(self):
        for rec in self:
            rec.state = 'rechazado'
            rec.line_cargo_id.message_post('Cargo por '+str(rec.name)+" fue rechazado")

    @api.multi
    def action_aprove(self):
        for rec in self:
            rec.state = 'aprobado'
            rec.line_cargo_id.message_post('Cargo por '+str(rec.name)+" fue aprobado")

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




