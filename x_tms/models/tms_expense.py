# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from __future__ import division

from datetime import datetime, date, time, timedelta
import tempfile
import base64
import os

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from . import amount_to_text

class tms_categories_events(models.Model):


    _name = 'hr.employee.category'
    name = fields.Char('Etiqueta del empleado')
    
    employee_salary_ids = fields.One2many("hr.employee.salary", "hr_emp_cat_id", string="Detalles de salario")


class ExpenseDiferences(models.Model):
    _name = "expense.diference"
    name = fields.Char(string="Concepto")
    account_ids = fields.Many2one('account.account', string='Cuenta')
    tipo = fields.Selection([('reembolso','Reembolso'),('sobrante','Cambio')], string="Tipo")
    valor = fields.Float(string="Valor")
    product_id = fields.Many2one('product.product',string='Producto')
    expense_id = fields.Many2one("tms.expense")


class ExpenseFuelDiferences(models.Model):
    _name = "tms.fuel.diference"
    name = fields.Char(string="Mercancia")
    descripcion = fields.Char(string="Descripción")
    litros = fields.Float(string="Litros")
    importe = fields.Float(string="Importe")
    fecha = fields.Char(string="Fecha")
    hora = fields.Char(string="Hora")
    unidad = fields.Char(string="Unidad")
    expense_id = fields.Many2one("tms.expense")



class TmsExpense(models.Model):
    _name = 'tms.expense'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Travel Expenses'
    _order = 'name desc'

    name = fields.Char(readonly=True)
    expense_dif_ids = fields.One2many("expense.diference", "expense_id")
    fuel_dif_ids = fields.One2many("tms.fuel.diference", "expense_id")
    file_fuel = fields.Binary(string="Archivo de combustible.")
    filenamef = fields.Char('file name')

    employee_salary_ids = fields.One2many("hr.employee.salary", "expense_id", string="Detalles de salario")


    operating_unit_id = fields.Many2one(
        'operating.unit', string="Operating Unit", required=True,default=lambda self: self.env['operating.unit'].search([('name','=','Mexico')], limit=1).id or self.env['operating.unit'].search([('name','=','México')], limit=1).id or '')
    employee_id = fields.Many2one(
        'hr.employee', 'Driver')
    travel_ids = fields.Many2many('tms.travel',string='Travels')
    unit_id = fields.Many2one(
        'fleet.vehicle', 'Unit', required=True)

    

 

    date_inicio = fields.Datetime(string='Fecha Prevista', compute='_compute_date_inicio')
    date_fin = fields.Datetime(string='Fecha Prevista', compute='_compute_date_fin')
    @api.depends('travel_ids.date','date')
    def _compute_date_inicio(self):        
        for order in self:
            min_date = False
            for line in order.travel_ids:
                if not min_date or line.date < min_date:
                    min_date = line.date
            if min_date:
                order.date_inicio = min_date
            else:
                order.date_inicio = order.date

    @api.depends('travel_ids.date','date')
    def _compute_date_fin(self):        
        for order in self:
            min_date = False
            for line in order.travel_ids:
                if not min_date or line.date > min_date:
                    min_date = line.date
            if min_date:
                order.date_fin = min_date
            else:
                order.date_fin = order.date


    odoo_inicio = fields.Float(string='odometro inicial', compute='_compute_odoo_inicio')
    odoo_fin = fields.Float(string='odometro final', compute='_compute_odoo_fin')
    @api.depends('travel_ids.odometro_inicial')
    def _compute_odoo_inicio(self):        
        for order in self:
            min_odoo = False
            for line in order.travel_ids:
                if not min_odoo or line.odometro_inicial < min_odoo:
                    min_odoo = line.odometro_inicial
            if min_odoo:
                order.odoo_inicio = min_odoo
            else:
                order.odoo_inicio = 0.0
                
    @api.depends('travel_ids.odometro_final')
    def _compute_odoo_fin(self):        
        for order in self:
            min_odoo = False
            for line in order.travel_ids:
                if not min_odoo or line.odometro_final > min_odoo:
                    min_odoo = line.odometro_final
            if min_odoo:
                order.odoo_fin = min_odoo
            else:
                order.odoo_fin = 0.0
      


    
    @api.onchange('file_fuel','unit_id')
    def onchange_file_fuel(self):
        if self.file_fuel and self.unit_id:
            data = base64.decodestring(self.file_fuel)
            fobj = tempfile.NamedTemporaryFile(delete=False)
            fname = fobj.name
            fobj.write(data)
            fobj.close()
            image = open(fname,"r")
            cont = 0
            line_ids = []
            res = {'value':{
                    'fuel_dif_ids':[],
                }
            }
            for x in image:
                if cont>3:
                    lista = x.split(",")
                    if self.unit_id.name == lista[0]:
                        if len(lista) > 32:
                            if float(lista[12]) > 0:
                                f = lista[9]
                                ff = lista[8]
                                date = ff[6:]+"-"+ff[3:5]+"-"+ff[:-8] + " " + f[:-3]
                                print(date)
                                if date >= self.start_date and date <= self.end_date:
                                    print("*********FECHAS********")
                                    print(self.start_date)
                                    print(date)
                                    print(self.end_date)
                                    b = lista[6]
                                    c = lista[7]
                                    impo = str(b + c)
                                    if impo[0].isdigit():
                                        impo = impo
                                    else:
                                        impo = impo[1:-1]
                                    print(impo)
                                    line = {
                                    'name':lista[10],
                                    'descripcion':lista[11],
                                    'litros':float(lista[12]),
                                    'importe':float(impo),
                                    'fecha':lista[8],
                                    'hora':lista[9],
                                    'unidad':lista[0],
                                    'expense_id':self.id,
                                    }
                                    line_ids += [line]
                            
                        else:
                            a = lista[11]
                            aa = lista[6]
                            if float(a) > 0:
                                f = lista[8]
                                ff = lista[7]
                                date = ff[6:]+"-"+ff[3:5]+"-"+ff[:-8] + " " + f[:-3]
                                if date >= self.start_date and date <= self.end_date:
                                    print("*********FECHAS********")
                                    print(self.start_date)
                                    print(date)
                                    print(self.end_date)
                                    line = {
                                    'name':lista[9],
                                    'descripcion':lista[10],
                                    'litros':float(a),
                                    'importe':float(aa),
                                    'fecha':lista[7],
                                    'hora':lista[8],
                                    'unidad':lista[0],
                                    'expense_id':self.id,
                                    }
                                    line_ids += [line]

                cont += 1
            res['value'].update({
                'fuel_dif_ids': line_ids,
            })
            return res
        else:
            line_ids = []
            res = {'value':{
                    'fuel_dif_ids':[],
                }
            }
            return res

    currency_id = fields.Many2one(
        'res.currency', 'Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id)
    company_id = fields.Many2one(
        'res.company', string="Company",
        default=lambda self: self.env.user.company_id)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled')], 'Expense State', readonly=True,
        help="Gives the state of the Travel Expense. ",
        default='draft')
    date = fields.Date(required=True, default=fields.Date.context_today)
    expense_line_ids = fields.One2many(
        'tms.expense.line', 'expense_id', 'Expense Lines')
    amount_real_expense = fields.Float(
        compute='_compute_amount_real_expense',
        string='Expenses',
        store=True)
    amount_made_up_expense = fields.Float(
        compute='_compute_amount_made_up_expense',
        string='Fake Expenses',
        store=True)
    fuel_qty = fields.Float(
        compute='_compute_fuel_qty')
    amount_fuel = fields.Float(
        compute='_compute_amount_fuel',
        string='Cost of Fuel',
        store=True)
    amount_fuel_cash = fields.Float(
        compute='_compute_amount_fuel_cash',
        string='Fuel in Cash',
        store=True)
    amount_refund = fields.Float(
        compute='_compute_amount_refund',
        string='Refund',
        store=True)
    amount_other_income = fields.Float(
        compute='_compute_amount_other_income',
        string='Other Income',
        store=True)
    amount_salary = fields.Float(
        compute='_compute_amount_salary',
        string='Salary',
        store=True)
    amount_net_salary = fields.Float(
        compute='_compute_amount_net_salary',
        string='Net Salary',
        store=True)
    amount_salary_retention = fields.Float(
        compute='_compute_amount_salary_retention',
        string='Salary Retentions',
        store=True)
    amount_salary_discount = fields.Float(
        compute='_compute_amount_salary_discount',
        string='Salary Discounts',
        store=True)
    amount_loan = fields.Float(
        compute='_compute_amount_loan',
        string='Loans',
        store=True)
    amount_advance = fields.Float(
        compute='_compute_amount_advance',
        string='Advances',
        store=True)
    amount_balance = fields.Float(
        compute='_compute_amount_balance',
        string='Balance',
        store=True)
    amount_tax_total = fields.Float(
        compute='_compute_amount_tax_total',
        string='Taxes (All)',
        store=True)
    amount_tax_real = fields.Float(
        compute='_compute_amount_tax_real',
        string='Taxes (Real)',
        store=True)
    amount_total_real = fields.Float(
        compute='_compute_amount_total_real',
        string='Total (Real)',
        store=True)
    amount_total_total = fields.Float(
        compute='_compute_amount_total_total',
        string='Total (All)',
        store=True)
    amount_subtotal_real = fields.Float(
        compute='_compute_amount_subtotal_real',
        string='SubTotal (Real)',
        store=True)
    amount_subtotal_total = fields.Float(
        string='SubTotal (All)',
        compute='_compute_amount_subtotal_total',
        store=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')
    last_odometer = fields.Float('Last Read')
    vehicle_odometer = fields.Float()
    current_odometer = fields.Float(
        string='Current Real',
        compute='_compute_current_odometer')
    odometer_log_id = fields.Many2one(
        'fleet.vehicle.odometer', 'Odometer Record')
    notes = fields.Text()
    move_id = fields.Many2one(
        'account.move', 'Journal Entry', readonly=True,
        help="Link to the automatically generated Journal Items.",
        ondelete='restrict',)
    paid = fields.Boolean(
        compute='_compute_paid',
        store=True,
        readonly=True)
    advance_ids = fields.One2many(
        'tms.advance', 'expense_id', string='Advances', readonly=True)
    loan_ids = fields.One2many('tms.expense.loan', 'expense_id',
                               string='Loans', readonly=True)
    fuel_qty_real = fields.Float(
        help="Fuel Qty computed based on Distance Real and Global Fuel "
        "Efficiency Real obtained by electronic reading and/or GPS")
    fuel_diff = fields.Float(
        string="Fuel Difference",
        help="Fuel Qty Difference between Fuel Vouchers + Fuel Paid in Cash "
        "versus Fuel qty computed based on Distance Real and Global Fuel "
        "Efficiency Real obtained by electronic reading and/or GPS"
        # compute=_get_fuel_diff
    )
    fuel_log_ids = fields.One2many(
        'fleet.vehicle.log.fuel', 'expense_id', string='Fuel Vouchers')
    start_date = fields.Datetime()
    end_date = fields.Datetime()
    fuel_efficiency = fields.Float(
        readonly=True,
        compute="_compute_fuel_efficiency")
    payment_move_id = fields.Many2one(
        'account.move', string='Payment Entry',
        readonly=True,)
    travel_days = fields.Char(
        compute='_compute_travel_days',
    )
    distance_loaded = fields.Float(
        compute='_compute_distance_expense',
    )
    distance_empty = fields.Float(
        compute='_compute_distance_expense',
    )
    distance_loaded_real = fields.Float(
    compute='_compute_distance_expense_dos',
    )
    distance_empty_real = fields.Float(
         compute='_compute_distance_expense_dos',
    )
    distance_routes = fields.Float(
        compute='_compute_distance_routes',
        string='Distance from routes',
        help="Routes Distance", readonly=True)
    distance_real = fields.Float(
        compute='_compute_distance_expense_dos',
        help="Route obtained by electronic reading and/or GPS")
    income_km = fields.Float(
        compute='_compute_income_km',
    )
    expense_km = fields.Float(
        compute='_compute_expense_km',
    )
    percentage_km = fields.Float(
        'Productivity Percentage',
        compute='_compute_percentage_km',
    )
    fuel_efficiency_real = fields.Float(
          compute='_compute_distance_expense',
    )
    #convertir numero a texto
    amount_to_text = fields.Char(compute='_get_amount_to_text', string='Monto en Texto', readonly=True,
                                help='Amount of the invoice in letter')
    @api.one
    @api.depends('amount_balance')
    def _get_amount_to_text(self):
        self.amount_to_text = amount_to_text.get_amount_to_text(self, self.amount_balance)

    #cuenta_banc = fields.Char(string="Cuenta Bancaria", related="payment_move_id.cuenta_banc")
    cuenta_b = fields.Many2one("res.partner.bank", string="Cuenta Bancaria", related="payment_move_id.cuenta_b")
    n_transaccion = fields.Char(string="Número de Transacción", related="payment_move_id.n_transaccion")
    adjunto_compro = fields.Binary(string="Comprobante", related="payment_move_id.adjunto_compro")
    filename = fields.Char('file name', related="payment_move_id.filename")

    force_perceps = fields.Boolean(string="Forzar Percepciones/Deducciones")
    periodo_force_perceps = fields.Selection([('sem','Semanal'),('quin','Quincenal'),('men','Mensual')], string="Periodo Percepciones")

    force_info = fields.Boolean(string="Forzar Infonavit")
    periodo_force_info = fields.Selection([('sem','Semanal'),('quin','Quincenal'),('men','Mensual')], string="Periodo Percepciones")



    #@api.multi
    # @api.onchange('travel_ids')
    # def onchange_travel_ids(self):
    #     actuales = []
    #     nuevos = []
    #     actual = {}
    #     nuevo = {}
    #     merma = 0 #Merma de viajes de la liquidación.
    #     saldo = 0 #Saldo pendiente de la ultima liquidación.
    #     existe_merma = False
    #     existe_saldo = False
        
    #     #raise ValidationError("Error de validacion")
        
    #     #------------------------------------------------------------------------------------------
    #     # Deducciones
    #     #------------------------------------------------------------------------------------------
    #     #Obtiene las deducciones/percepciones existentes.
    #     for a in self.employee_salary_ids:
    #         if a.name.strip().lower() == "merma":
    #             existe_merma = True
    #             #_logger.info("Existe merma!!")

    #         if a.name.strip().lower() == "saldo pendiente":
    #             existe_saldo = True
    #             #_logger.info("Existe saldo!!")
    #         productd_id = self.env['product.product'].search([
    #                 ('name', '=', 'Merma')],limit=1)   
    #         actual = {
    #             'name': a.name,
    #             'tipo': a.tipo,
    #             'product_id': productd_id.id,
    #             'monto': a.monto,
    #             'hr_emp_cat_id': a.hr_emp_cat_id,
    #             'expense_id': a.expense_id,
    #             'periodo': a.periodo,
    #             'account_ids': a.account_ids
    #         }
    #         actuales.append(actual)


    #     #Obtener la suma de las mermas de los viajes relacionados con la liquidación.
    #     merma = 0
    #     for v in self.travel_ids:
    #         #_logger.info(v)
    #         merma += v.merma_cobrar_pesos
    #         #_logger.info("Merma $: "+str(merma))
            
    #     liquidaciones_obj = None
    #     liquidaciones_dat = None
    #     #Buscar la última liquidación con saldo.
    #     liquidaciones_obj = self.env['tms.expense']
    #     if self.unit_id and self.employee_id and self._origin:
    #         liquidaciones_dat = liquidaciones_obj.search([('unit_id', '=', self.unit_id.id), ('employee_id', '=', self.employee_id.id), ('id', '<', self._origin.id), ('amount_balance', '<', 0), ('state', '=', 'confirmed')], limit=1, order="id desc")
    #     #_logger.info(">>Ultimas liquidaciones: "+str(liquidaciones_dat))
    #     if liquidaciones_dat and liquidaciones_dat.amount_balance < 0:
    #         saldo = abs(liquidaciones_dat.amount_balance)

    #     #Si hay merma generar una deduccion de dicha merma.
    #     # if merma > 0:
    #     #     if existe_merma:
    #     #         for a in actuales:
    #     #             if a.get('name', '').strip().lower() == "merma":
    #     #                 a['monto'] = merma
    #     #     else:
    #     #         productd_id = self.env['product.product'].search([
    #     #             ('name', '=', 'Merma')],limit=1)   
    #     #         nuevo = {
    #     #             'name': "Merma",
    #     #             'account_ids': False,
    #     #             'product_id': productd_id.id,
    #     #             'tipo': 'deduccion',
    #     #             'monto': merma,
    #     #             'periodo': "sem",
    #     #             'expense_id': self._origin.id
    #     #         }
    #     #         actuales.append(nuevo)
    #     # Si hay saldo pendiente generar una deduccion de dicha saldo.
    #     if saldo > 0:
    #         if existe_saldo:
    #             for a in actuales:
    #                 if a.get('name', '').strip().lower() == "saldo pendiente":
    #                     a['monto'] = saldo
    #         else:
    #             nuevo = {
    #                 'name': "Saldo pendiente",
    #                 'account_ids': False,
                  
    #                 'tipo': 'deduccion',
    #                 'monto': saldo,
    #                 'periodo': "sem",
    #                 'expense_id': self._origin.id
    #             }
    #             actuales.append(nuevo)
        
    #     if merma <= 0:
    #         #_logger.info("Actuales:"+str(actuales))
    #         for a in reversed(actuales):
    #             if a.get('name', '').strip().lower() == "merma":
    #                 actuales.remove(a)

    #     if saldo <= 0:
    #         #_logger.info("Actuales:"+str(actuales))
    #         for a in reversed(actuales):
    #             if a.get('name', '').strip().lower() == "saldo pendiente":
    #                 actuales.remove(a)
        
    #     #Actualiza todos los registros.
    #     for ac in actuales:
    #         #if ac.get('name','').
    #         nuevos += [(0, 0, ac)]

    #     self.update({'employee_salary_ids': nuevos})

    @api.depends('travel_ids')
    def _compute_income_km(self):
        for rec in self:
            rec.income_km = 0.0
            rec.expense = 0.0
            subtotal_waybills = 0.0
            for travel in rec.travel_ids:
                for waybill in travel.waybill_ids:
                    subtotal_waybills += waybill.amount_untaxed
            try:
                rec.income_km = subtotal_waybills / rec.distance_real
            except ZeroDivisionError:
                rec.income_km = 0.0

    @api.depends('distance_real', 'amount_subtotal_real')
    def _compute_expense_km(self):
        for rec in self:
            try:
                rec.expense_km = rec.amount_subtotal_real / rec.distance_real
            except ZeroDivisionError:
                rec.expense_km = 0.0

    @api.depends('income_km', 'expense_km')
    def _compute_percentage_km(self):
        for rec in self:
            try:
                rec.percentage_km = rec.income_km / rec.expense_km
            except ZeroDivisionError:
                rec.percentage_km = 0.0

    @api.depends('travel_ids')
    def _compute_distance_expense(self):
        for rec in self:
            for travel in rec.travel_ids:
                rec.distance_loaded += travel.distance_loaded
                rec.distance_empty += travel.distance_empty
                rec.fuel_efficiency_real += travel.fuel_efficiency_travel

    def _compute_distance_expense_dos(self):
        for rec in self:
            rec.distance_loaded_real += rec.distance_loaded
            rec.distance_empty_real += rec.distance_empty
            rec.distance_real += rec.distance_routes


    @api.depends('start_date', 'end_date')
    def _compute_travel_days(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                strp_start_date = datetime.strptime(
                    rec.start_date, "%Y-%m-%d %H:%M:%S")
                strp_end_date = datetime.strptime(
                    rec.end_date, "%Y-%m-%d %H:%M:%S")
                difference = strp_end_date - strp_start_date
                days = int(difference.days) + 1
                hours = int(difference.seconds / 3600)
                mins = int((difference.seconds - (hours * 3600))/60)
                seconds = difference.seconds - ((hours * 3600) + (mins * 60))
                if hours < 10:
                    hours = '0' + str(hours)
                if mins < 10:
                    mins = '0' + str(mins)
                if seconds < 10:
                    seconds = '0' + str(seconds)
                total_string = (
                    str(days) + _('Day(s), ') +
                    str(hours) + ':' +
                    str(mins) + ':' +
                    str(seconds))
                rec.travel_days = total_string

    @api.depends('payment_move_id')
    def _compute_paid(self):
        for rec in self:
            if rec.payment_move_id:
                rec.paid = True

    @api.depends('fuel_qty', 'distance_real')
    def _compute_fuel_efficiency(self):
        for rec in self:
            if rec.distance_real and rec.fuel_qty:
                rec.fuel_efficiency = rec.distance_real / rec.fuel_qty

    @api.depends('travel_ids','fuel_qty')
    def _compute_fuel_qty(self):
        qty = 0.0
        for rec in self:
            for travel in rec.travel_ids:
                qty += (travel.combustible1+travel.combustible2)
            rec.fuel_qty = qty

    @api.depends('travel_ids', 'expense_line_ids')
    def _compute_amount_fuel(self):
        for rec in self:
            rec.amount_fuel = 0.0
            for line in rec.fuel_log_ids:
                rec.amount_fuel += (
                    line.price_subtotal +
                    line.special_tax_amount)

    @api.depends('expense_line_ids')
    def _compute_amount_fuel_cash(self):
        for rec in self:
            rec.amount_fuel_cash = 0.0
            for line in rec.expense_line_ids:
                if line.line_type == 'fuel_cash':
                    rec.amount_fuel_cash += (
                        line.price_subtotal +
                        line.special_tax_amount)

    @api.depends('expense_line_ids','expense_dif_ids')
    def _compute_amount_refund(self):
        for rec in self:
            rec.amount_refund = 0.0
            for line in rec.expense_line_ids:
                if line.line_type == 'refund':
                    rec.amount_refund += line.price_total
            # for line in rec.expense_dif_ids:
            #     if line.tipo == 'reembolso':
            #         rec.amount_refund += line.valor

    @api.depends('expense_line_ids')
    def _compute_amount_other_income(self):
        for rec in self:
            rec.amount_other_income = 0.0
            for line in rec.expense_line_ids:
                if line.line_type == 'other_income':
                    rec.amount_other_income += line.price_total

    @api.depends('expense_line_ids')
    def _compute_amount_salary(self):
        for rec in self:
            rec.amount_salary = 0.0
            for line in rec.expense_line_ids:
                if line.line_type == 'salary':
                    rec.amount_salary += line.price_total

    @api.depends('expense_line_ids','expense_dif_ids')
    def _compute_amount_salary_discount(self):
        for rec in self:
            rec.amount_salary_discount = 0
            # for l in rec.employee_salary_ids:
            #     if l.name == 'Merma':
            #         print("*********************************************************************",-l.monto)
            #         rec.amount_salary_discount += -l.monto
            for line in rec.expense_line_ids:
                if line.line_type == 'salary_discount':
                    print("*********************************************************************",line.price_total)
                    rec.amount_salary_discount += line.price_total
            # for line in rec.expense_dif_ids:
            #     if line.tipo != 'reembolso':
            #         rec.amount_salary_discount += (line.valor * -1)

    @api.depends('expense_line_ids')
    def _compute_amount_loan(self):
        for rec in self:
            rec.amount_loan = 0
            for line in rec.expense_line_ids:
                if line.line_type == 'loan':
                    rec.amount_loan += line.price_total

    @api.depends('expense_line_ids')
    def _compute_amount_made_up_expense(self):
        for rec in self:
            rec.amount_made_up_expense = 0
            for line in rec.expense_line_ids:
                if line.line_type == 'made_up_expense':
                    rec.amount_made_up_expense += line.price_total

    @api.depends('expense_line_ids')
    def _compute_amount_real_expense(self):
        for rec in self:
            rec.amount_real_expense = 0
            for line in rec.expense_line_ids:
                if line.line_type == 'real_expense':
                    if line.unit_price < 0:
                        rec.amount_real_expense += line.price_subtotal * -1


    amount_percepciones = fields.Float(string="Total Percepciones", compute="_compute_amount_percep", store=True)
    amount_deducciones = fields.Float(string="Total Deducciones", compute="_compute_amount_deduc", store=True)
    
    @api.depends('employee_salary_ids','amount_percepciones')
    def _compute_amount_percep(self):
        for rec in self:
            for x in rec.employee_salary_ids:
                if x.tipo == 'percepcion':
                    rec.amount_percepciones += x.monto

    @api.onchange('employee_salary_ids')
    def onchange_amount_percep(self):
        for rec in self:
            for x in rec.employee_salary_ids:
                if x.tipo == 'percepcion':
                    rec.amount_percepciones += x.monto

    @api.depends('employee_salary_ids','amount_deducciones')
    def _compute_amount_deduc(self):
        for rec in self:
            for x in rec.employee_salary_ids:
                if x.tipo == 'deduccion':
                    rec.amount_deducciones += x.monto

    @api.onchange('employee_salary_ids')
    def onchange_amount_deduc(self):
        for rec in self:
            for x in rec.employee_salary_ids:
                if x.tipo == 'deduccion':
                    rec.amount_deducciones += x.monto


    @api.multi
    def get_nomina(self):
        for rec in self:
            rec.employee_salary_ids.search([
                ('expense_id', '=', rec.id)]).unlink()
            today = datetime(int(rec.date[:4]),int(rec.date[5:7]),int(rec.date[8:10]))
            week_day = today.weekday()
            month = int(rec.date[5:7])
            month_day = int(rec.date[8:10])
            DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            # week_day = today.weekday()
            # month = int(rec.date[5:7])
            # month_day = int(rec.date[8:10])
            f_i = datetime.strptime(rec.start_date, DATETIME_FORMAT)
            f_f = datetime.strptime(rec.end_date, DATETIME_FORMAT)
            v = 0
            q = 0
            m = 0
            while f_i <= f_f:
                if f_i.weekday() == 4:
                    v += 1
                if int(f_i.strftime("%d")) == 30:
                    m += 1
                if (int(f_i.strftime("%d")) == 15 or int(f_i.strftime("%d")) == 30):
                    q += 1
                f_i += timedelta(days=1)



            for x in rec.employee_id.employee_category_id.employee_salary_ids:
                print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$",x.product_id.id)
                if x.periodo == 'sem' and v > 0:
                    rec.employee_salary_ids.create({
                    'name': x.name + ", " + str(v) +" semanas",
                    'product_id': x.product_id.id,
                    'tipo': x.tipo,
                    'monto': x.monto * v,
                    'periodo': x.periodo,
                    'expense_id': rec.id
                    })
                if x.periodo == 'quin' and q > 0:
                    rec.employee_salary_ids.create({
                    'name': x.name+ ", " + str(q) + " quincenas",
                    'product_id': x.product_id.id,
                    'tipo': x.tipo,
                    'monto': x.monto * q,
                    'periodo': x.periodo,
                    'expense_id': rec.id
                    })
                if x.periodo == 'men' and m > 0:
                    rec.employee_salary_ids.create({
                    'name': x.name + ", " + str(m) +" meses",
                    'product_id': x.product_id.id,
                    'tipo': x.tipo,
                    'monto': x.monto * m,
                    'periodo': x.periodo,
                    'expense_id': rec.id
                    })
            if self.employee_id.monto_info > 0.0:
                product_id_info = self.env['product.product'].search([
                ('name', '=', 'INFONAVIT')],limit=1)
                if self.employee_id.periodo_info == 'sem' and v > 0:
                    rec.employee_salary_ids.create({
                    'name':"Infonavit" + ", " + str(v) +" semanas",
                    'product_id': product_id_info.id,
                    'tipo': 'deduccion',
                    'monto': self.employee_id.monto_info * v,
                    'periodo': self.employee_id.periodo_info,
                    'expense_id': rec.id
                    })
                if self.employee_id.periodo_info == 'quin' and q > 0:
                    rec.employee_salary_ids.create({
                    'name': "Infonavit"+ ", " + str(q) + " quincenas",
                    'product_id': product_id_info.id,
                    'tipo': 'deduccion',
                    'monto': self.employee_id.monto_info * q,
                    'periodo': self.employee_id.periodo_info,
                    'expense_id': rec.id
                    })
                if self.employee_id.periodo_info == 'men' and m > 0:
                    rec.employee_salary_ids.create({
                    'name': "Infonavit" + ", " + str(m) +" meses",
                    'product_id': product_id_info.id,
                    'tipo': 'deduccion',
                    'monto': self.employee_id.monto_info * m,
                    'periodo': self.employee_id.periodo_info,
                    'expense_id': rec.id
                    })
                    
            merma = 0
            for v in self.travel_ids:
                #_logger.info(v)
                merma += v.merma_cobrar_pesos
                #_logger.info("Merma $: "+str(merma))\
            int(merma)
            print("'.'.''.'.'.'.'.'.'.'.'.'.'",merma)
            if merma > 0:                
           
                productd_id = self.env['product.product'].search([
                    ('name', '=', 'Merma')],limit=1)   
                rec.employee_salary_ids.create({
                    'name': "Merma",                    
                    'product_id': productd_id.id,
                    'tipo': 'deduccion',
                    'monto': merma,
                    'periodo': "sem",
                    'expense_id': rec.id
                })


            liquidaciones_obj = None
            liquidaciones_dat = None
            #Buscar la última liquidación con saldo.
            saldo = 0
            liquidaciones_obj = self.env['tms.expense']
            if self.unit_id and self.employee_id and rec.id:
                liquidaciones_dat = liquidaciones_obj.search([('unit_id', '=', self.unit_id.id), ('employee_id', '=', self.employee_id.id), ('id', '<', rec.id), ('amount_balance', '<', 0), ('state', '=', 'confirmed')], limit=1, order="id desc")
            #_logger.info(">>Ultimas liquidaciones: "+str(liquidaciones_dat))
            if liquidaciones_dat and liquidaciones_dat.amount_balance < 0:
                saldo = abs(liquidaciones_dat.amount_balance)

            if saldo > 0:
                productd_id = self.env['product.product'].search([
                    ('name', '=', 'SALDO PENDIENTE')],limit=1)               
                rec.employee_salary_ids.create({
                    'name': "Saldo pendiente",
                    'product_id': productd_id.id,         
                    'tipo': 'deduccion',
                    'monto': saldo,
                    'periodo': "sem",
                    'expense_id': rec.id
                })
               

            #rec.get_travel_info()
    

    @api.depends('travel_ids', 'expense_line_ids','expense_dif_ids')
    def _compute_amount_subtotal_real(self):
        for rec in self:
            rec.amount_subtotal_real = (
                rec.amount_salary +
                rec.amount_salary_discount +
                rec.amount_real_expense +
                rec.amount_salary_retention +
                rec.amount_loan +
                rec.amount_fuel_cash +
                rec.amount_other_income
                )

    @api.depends('travel_ids', 'expense_line_ids','expense_dif_ids')
    def _compute_amount_total_real(self):
        for rec in self:
            rec.amount_total_real = (
                rec.amount_subtotal_real +
                rec.amount_tax_real)

    @api.depends('travel_ids', 'expense_line_ids','expense_dif_ids')
    def _compute_amount_balance(self):
        for rec in self:
            rec.amount_balance = (rec.amount_total_real -
                                  rec.amount_advance)

    @api.depends('travel_ids')
    def _compute_amount_net_salary(self):
        for rec in self:
            rec.amount_net_salary = 1.0

    @api.depends('expense_line_ids')
    def _compute_amount_salary_retention(self):
        for rec in self:
            for line in rec.expense_line_ids:
                if line.line_type == 'salary_retention':
                    rec.amount_salary_retention += line.price_total

    @api.depends('travel_ids', 'expense_line_ids')
    def _compute_amount_advance(self):
        for rec in self:
            rec.amount_advance = 0
            for travel in rec.travel_ids:
                for advance in travel.advance_ids:
                    #and advance.adelanto_factor
                    if advance.payment_move_id and advance.to_expense == True:
                        rec.amount_advance += advance.amount

    @api.depends('travel_ids', 'expense_line_ids')
    def _compute_amount_tax_total(self):
        for rec in self:
            rec.amount_tax_total = 0
            for travel in rec.travel_ids:
                for fuel_log in travel.fuel_log_ids:
                    rec.amount_tax_total += fuel_log.tax_amount
            rec.amount_tax_total += rec.amount_tax_real

    @api.depends('expense_line_ids')
    def _compute_amount_tax_real(self):
        for rec in self:
            rec.amount_tax_real = 0
            for line in rec.expense_line_ids:
                if line.line_type == 'real_expense':
                    rec.amount_tax_real += line.tax_amount

    @api.depends('travel_ids', 'expense_line_ids')
    def _compute_amount_subtotal_total(self):
        for rec in self:
            rec.amount_subtotal_total = 0
            for travel in rec.travel_ids:
                for fuel_log in travel.fuel_log_ids:
                    rec.amount_subtotal_total += (
                        fuel_log.price_subtotal +
                        fuel_log.special_tax_amount)
            for line in rec.expense_line_ids:
                if line.line_type == 'real_expense':
                    rec.amount_subtotal_total += line.price_subtotal
            rec.amount_subtotal_total += rec.amount_balance

    @api.depends('travel_ids', 'expense_line_ids')
    def _compute_amount_total_total(self):
        for rec in self:
            rec.amount_total_total = (
                rec.amount_subtotal_total + rec.amount_tax_total +
                rec.amount_made_up_expense)

    @api.depends('travel_ids')
    def _compute_distance_routes(self):
        distance = 0.0
        for rec in self:
            for travel in rec.travel_ids:
                distance += travel.route_id.distance
            rec.distance_routes = distance

    @api.depends('travel_ids')
    def _compute_current_odometer(self):
        for rec in self:
            rec.current_odometer = rec.unit_id.odometer

    # @api.depends('travel_ids')
    # def _compute_distance_real(self):
    #     for rec in self:
    #         rec.distance_real = 1.0

    @api.model
    def create(self, values):
        expense = super(TmsExpense, self).create(values)
        sequence = expense.operating_unit_id.expense_sequence_id
        expense.name = sequence.next_by_id()
        return expense

    @api.multi
    def write(self, values):
        for rec in self:
            res = super(TmsExpense, self).write(values)
            #rec.get_travel_info()
            return res

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'confirmed':
                raise ValidationError(
                    _('You can not delete a travel expense'
                      'in status confirmed'))
            else:
                travels = self.env['tms.travel'].search(
                    [('expense_id', '=', rec.id)])
                for x in travels:
                    x.write({
                        'expense_id': False,
                        'state': 'done'
                    })
                advances = self.env['tms.advance'].search(
                    [('expense_id', '=', rec.id)])
                advances.write({
                    'expense_id': False,
                    'state': 'confirmed'
                })
                fuel_logs = self.env['fleet.vehicle.log.fuel'].search(
                    [('expense_id', '=', rec.id)])
                fuel_logs.write({
                    'expense_id': False,
                    'state': 'confirmed'
                })
                return super(TmsExpense, self).unlink()

    @api.multi
    def action_approved(self):
        for rec in self:
            rec.message_post(body=_('<b>Expense Approved.</b>'))
        self.state = 'approved'

    @api.multi
    def action_draft(self):
        for rec in self:
            rec.message_post(body=_('<b>Expense Drafted.</b>'))
        self.state = 'draft'

    @api.model
    def prepare_move_line(self, name, ref, account_id,
                          debit, credit, journal_id,
                          partner_id, operating_unit_id):
        return (0, 0, {
            'name': name,
            'ref': ref,
            'account_id': account_id,
            'debit': debit,
            'credit': credit,
            'journal_id': journal_id,
            'partner_id': partner_id,
            'operating_unit_id': operating_unit_id,
        })

    @api.model
    def create_fuel_vouchers(self, line):
        for rec in self:
            fuel_voucher = rec.env['fleet.vehicle.log.fuel'].create({
                'operating_unit_id': rec.operating_unit_id.id,
                'travel_id': line.travel_id.id,
                'vehicle_id': line.travel_id.unit_id.id,
                'product_id': line.product_id.id,
                'price_unit': line.unit_price,
                'price_subtotal': line.price_subtotal,
                'vendor_id': line.partner_id.id,
                'product_qty': line.product_qty,
                'tax_amount': line.tax_amount,
                'state': 'closed',
                'employee_id':  rec.employee_id.id,
                'price_total': line.price_total,
                'date': str(fields.Date.today()),
                'expense_control': True,
                'expense_id': rec.id,
                'ticket_number': line.invoice_number,
                })
            line.control = True
            return fuel_voucher

    @api.multi
    def higher_than_zero_move(self):
        for rec in self:
            move_lines = []
            invoices = []
            move_obj = rec.env['account.move']
            journal_id = rec.operating_unit_id.expense_journal_id.id
            advance_account_id = (
                rec.employee_id.
                tms_advance_account_id.id
            )
            negative_account = (
                rec.employee_id.
                tms_expense_negative_account_id.id
            )
            driver_account_payable = (
                rec.employee_id.
                address_home_id.property_account_payable_id.id
            )
            if not journal_id:
                raise ValidationError(
                    _('Warning! The expense does not have a journal'
                      ' assigned. \nCheck if you already set the '
                      'journal for expense moves in the Operating Unit.'))
            if not driver_account_payable:
                raise ValidationError(
                    _('Warning! The driver does not have a home address'
                      ' assigned. \nCheck if you already set the '
                      'home address for the employee.'))
            if not advance_account_id:
                raise ValidationError(
                    _('Warning! You must have configured the accounts'
                        'of the tms for the Driver'))
            # We check if the advance amount is higher than zero to create
            # a move line
            if rec.amount_advance > 0:
                move_line = rec.prepare_move_line(
                    _('Advance Discount'),
                    rec.name,
                    advance_account_id,
                    0.0,
                    rec.amount_advance,
                    journal_id,
                    rec.employee_id.address_home_id.id,
                    rec.operating_unit_id.id)
                move_lines.append(move_line)
            result = {
                'move_lines': move_lines,
                'invoices': invoices,
                'move_obj': move_obj,
                'journal_id': journal_id,
                'advance_account_id': advance_account_id,
                'negative_account': negative_account,
                'driver_account_payable': driver_account_payable
            }
            return result

    @api.multi
    def check_expenseline_invoice(self, line, result, product_account):
        print("check_expenseline_invoice eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")
        for rec in self:
            # We check if the expense line is an invoice to create it
            # and make the move line based in the total with taxes
            inv_id = False
            if line.is_invoice:
                inv_id = rec.create_supplier_invoice(line)
                inv_id.action_invoice_open()
                result['invoices'].append(inv_id)
                move_line = rec.prepare_move_line(
                    (rec.name + ' ' + line.name +
                     ' - Inv ID - ' + str(inv_id.id)),
                    (rec.name + ' - Inv ID - ' + str(inv_id.id)),
                    (line.partner_id.
                        property_account_payable_id.id),
                    (line.price_total if line.price_total > 0.0
                        else 0.0),
                    (line.price_total if line.price_total <= 0.0
                        else 0.0),
                    result['journal_id'],
                    line.partner_id.id,
                    rec.operating_unit_id.id)
            # if the expense line not be a invoice we make the move
            # line based in the subtotal
            elif (rec.employee_id.outsourcing and
                  line.product_id.tms_product_category in
                  ['salary', 'other_income', 'salary_discount']):
                continue
            else:
                move_line = rec.prepare_move_line(
                    rec.name + ' ' + line.name,
                    rec.name,
                    product_account,
                    (line.price_subtotal if line.price_subtotal > 0.0
                        else 0.0),
                    (line.price_subtotal * -1.0
                        if line.price_subtotal < 0.0
                        else 0.0),
                    result['journal_id'],
                    rec.employee_id.address_home_id.id,
                    rec.operating_unit_id.id)
                print("move_line 1 mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm")
            result['move_lines'].append(move_line)
            # we check the line tax to create the move line if
            # the line not be an invoice
            for tax in line.tax_ids:
                tax_account = tax.account_id.id
                if not tax_account:
                    raise ValidationError(
                        _('Warning !'),
                        _('Tax Account is not defined for '
                          'Tax %s (id:%d)') % (tax.name, tax.id,))
                tax_amount = line.tax_amount
                # We create a move line for the line tax
                if not line.is_invoice:
                    move_line = rec.prepare_move_line(
                        rec.name + ' ' + line.name,
                        rec.name,
                        tax_account,
                        (tax_amount if tax_amount > 0.0
                            else 0.0),
                        (tax_amount if tax_amount <= 0.0
                            else 0.0),
                        result['journal_id'],
                        rec.employee_id.address_home_id.id,
                        rec.operating_unit_id.id)
                    print("move_line 2 mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm")
                    result['move_lines'].append(move_line)

    @api.multi
    def create_expense_line_move_line(self, line, result):
        print("create_expense_line_move_line cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc")
        for rec in self:
            # We only need all the lines except the fuel and the
            # made up expenses
            if line.line_type == 'fuel' and not line.control:
                rec.create_fuel_vouchers(line)
            if line.line_type not in (
                    'made_up_expense', 'fuel', 'tollstations'):
                product_account11 = (
                    result['negative_account']
                    if (line.product_id.
                        tms_product_category == 'negative_balance')
                    else (line.product_id.
                          property_account_expense_id.id)
                    if (line.product_id.
                        property_account_expense_id.id)
                    else (line.product_id.categ_id.
                          property_account_expense_categ_id.id)
                    if (line.product_id.categ_id.
                        property_account_expense_categ_id.id)
                    else False)
                product_account=line.account_ids.id

                print("pppppppppppppppppppppppppppppppppppppppppppppppppppp",line.account_ids.id)
                print("pppppppppppppppppppppppppppppppppppppppppppppppppppp",product_account11)
                if not product_account:
                    raise ValidationError(
                        _('Warning ! Expense Account is not defined for'
                            ' product %s') % (line.product_id.name))
                self.check_expenseline_invoice(line, result, product_account)

    @api.multi
    def check_balance_value(self, result):
        print("check_balance_value vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
        for rec in self:
            print("ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",rec.name)
            balance = rec.amount_balance
            if (rec.employee_id.outsourcing and rec.expense_line_ids.filtered(
                    lambda x: x.line_type in ['other_income', 'salary'])):
                balance = (
                    balance - rec.amount_other_income -
                    rec.amount_salary) - sum(
                    rec.expense_line_ids.filtered(
                        lambda y: y.line_type == 'salary_discount').mapped(
                        'price_total'))
            if balance < 0:
                move_line = rec.prepare_move_line(
                    _('Negative Balance'),
                    rec.name,
                    result['negative_account'],
                    balance * -1.0,
                    0.0,
                    result['journal_id'],
                    rec.cuenta_b.id,
                    rec.operating_unit_id.id)
                
            else:
                move_line = rec.prepare_move_line(
                    rec.name,
                    rec.name,
                    result['driver_account_payable'],
                    0.0,
                    balance,
                    result['journal_id'],
                    rec.cuenta_b.id,
                    rec.operating_unit_id.id)
            result['move_lines'].append(move_line)

    @api.multi
    def reconcile_account_move(self, result):
        print("reconcile_account_move mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm")
        for rec in self:
            move = {
                'date': fields.Date.today(),
                'journal_id': result['journal_id'],
                'name': rec.name,
                'line_ids': [line for line in result['move_lines']],
                'partner_id': rec.env.user.company_id.id,
                'operating_unit_id': rec.operating_unit_id.id,
            }
            move_id = result['move_obj'].create(move)
            print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",move_id)
            if not move_id:
                raise ValidationError(
                    _('An error has occurred in the creation'
                        ' of the accounting move. '))
            move_id.post()
            # Here we reconcile the invoices with the corresponding
            # move line
            rec.reconcile_supplier_invoices(result['invoices'], move_id)
        rec.write(
            {
                'move_id': move_id.id,
                'state': 'confirmed'
            })

    @api.multi
    def action_confirm(self):
        print("action confirm aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        for rec in self:
            # if rec.move_id:
            #     raise ValidationError(
            #         _('You can not confirm a confirmed expense.'))
            # result = rec.higher_than_zero_move()
            # for line in rec.expense_line_ids:
            #     rec.create_expense_line_move_line(line, result)
            # # Here we check if the balance is positive or negative to create
            # # the move line with the correct values
            # rec.check_balance_value(result)
            #rec.reconcile_account_move(result)
            rec.write({'state': 'confirmed'})
            rec.message_post(body=_('<b>Expense Confirmed.</b>'))

    @api.multi
    def payment(self):
        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx_______________------")
        for rec in self:
            if rec.move_id:
                raise ValidationError(
                    _('You can not confirm a confirmed expense.'))
            result = rec.higher_than_zero_move()
            for line in rec.expense_line_ids:
                rec.create_expense_line_move_line(line, result)
            # Here we check if the balance is positive or negative to create
            # the move line with the correct values
            rec.check_balance_value(result)
            rec.reconcile_account_move(result)
            rec.write({'state': 'confirmed'})
            rec.message_post(body=_('<b>Expense Confirmed.</b>'))

    @api.multi
    def action_cancel(self):
        self.ensure_one()
        if self.paid:
            raise ValidationError(
                _('You cannot cancel an expense that is paid.'))
        if self.state == 'confirmed':
            for line in self.expense_line_ids:
                if line.invoice_id and line.line_type != 'fuel':
                    for move_line in line.invoice_id.move_id.line_ids:
                        if move_line.account_id.reconcile:
                            move_line.remove_move_reconcile()
                    line.invoice_id.write({
                        # TODO Make a separate module to delete oml data
                        'cfdi_fiscal_folio': False,
                        'xml_signed': False,
                        'reference': False,
                        })
                    line.invoice_id.signal_workflow('invoice_cancel')
                    line.invoice_id = False
            if self.move_id.state == 'posted':
                self.move_id.button_cancel()
            move_id = self.move_id
            self.move_id = False
            move_id.unlink()
        self.state = 'cancel'

    @api.multi
    def unattach_info(self):
        for rec in self:
            exp_no_travel = rec.expense_line_ids.search([
                ('expense_id', '=', rec.id),
                ('travel_id', '=', False)]).ids
            rec.expense_line_ids.search([
                ('expense_id', '=', rec.id),
                ('travel_id', 'not in', rec.travel_ids.ids),
                ('id', 'not in', exp_no_travel)]).unlink()
            rec.expense_line_ids.search([
                ('expense_id', '=', rec.id),
                ('control', '=', True)]).unlink()
            travels = self.env['tms.travel'].search(
                [('expense_id', '=', rec.id)])
            for t in travels:
                t.write({'expense_id': False, 'state': 'done'})
            advances = self.env['tms.advance'].search(
                [('expense_id', '=', rec.id)])
            advances.write({
                'expense_id': False,
                'state': 'confirmed'
            })
            fuel_logs = self.env['fleet.vehicle.log.fuel'].search(
                [('expense_id', '=', rec.id)])
            fuel_logs.write({
                'expense_id': False,
                'state': 'confirmed'
            })
            rec.expense_dif_ids.search([
                ('expense_id', '=', rec.id)]).unlink()
            # expense_dif_ids = self.env['expense.diference'].search([
            #     ('expense_id', '=', rec.id)
            #     ])
            # expense_dif_ids.unlink()

    @api.multi
    def create_advance_line(self, advance, travel):
        if advance.state not in ('confirmed', 'cancel'):
            raise ValidationError(_(
                'Oops! All the advances must be confirmed'
                ' or cancelled \n '
                'Name of advance not confirmed or cancelled: ' +
                advance.name +
                '\n State: ' + advance.state))
        if not advance.paid:
            if advance.move_id.matched_percentage == 1.0:
                advance_move = advance.move_id.line_ids[-1]
                if advance_move.credit > 0:
                    move_lines = advance.move_id.line_ids[-1]
                    reconcile_move = move_lines.full_reconcile_id
                    for line in reconcile_move.reconciled_line_ids:
                        if line.journal_id.type == 'bank':
                            move_id = line.move_id.id
                advance.write(
                    {'paid': True, 'payment_move_id': move_id})
        if not advance.paid and advance.state == 'confirmed':
            raise ValidationError(_(
                'Oops! All the advances must be paid'
                '\n Name of advance not paid: ' +
                advance.name))
        if (advance.auto_expense and
                advance.state == 'confirmed'):
            self.expense_line_ids.create({
                'name': _("Advance: ") + str(advance.name),
                'travel_id': travel.id,
                'expense_id': self.id,
                'line_type': "real_expense",
                'product_id': advance.product_id.id,
                'product_qty': 1.0,
                'unit_price': advance.amount,
                'control': True
            })
        if advance.state != 'cancel':
            advance.write({
                'state': 'closed',
                'expense_id': self.id
            })

    @api.multi
    def create_fuel_line(self, fuel_log, travel):
        for rec in self:
            if (fuel_log.state != 'confirmed' and
                    fuel_log.state != 'closed'):
                raise ValidationError(_(
                    'Oops! All the voucher must be confirmed'
                    '\n Name of voucher not confirmed: ' +
                    fuel_log.name +
                    '\n State: ' + fuel_log.state))
            else:
                # fuel_expense = rec.expense_line_ids.create({
                #     'name': _(
                #         "Fuel voucher: ") + str(fuel_log.name),
                #     'travel_id': travel.id,
                #     'expense_id': rec.id,
                #     'line_type': 'fuel',
                #     'product_id': fuel_log.product_id.id,
                #     'product_qty': fuel_log.product_qty,
                #     'product_uom_id': (
                #         fuel_log.product_id.uom_id.id),
                #     'unit_price': fuel_log.price_total,
                #     'is_invoice': fuel_log.invoice_paid,
                #     'invoice_id': fuel_log.invoice_id.id,
                #     'control': True,
                #     'partner_id': fuel_log.vendor_id.id or False,
                #     'date': fuel_log.date,
                #     'invoice_number': fuel_log.ticket_number,
                # })
                # if fuel_log.expense_control:
                #     fuel_expense.name = fuel_expense.product_id.name
                fuel_log.write({
                    'state': 'closed',
                    'expense_id': rec.id
                })

    @api.multi
    def create_salary_line(self, travel):
        for rec in self:
            product_id = self.env['product.product'].search([
                ('tms_product_category', '=', 'salary')])
            if not product_id:
                raise ValidationError(_(
                    'Oops! You must create a product for the'
                    ' diver salary with the Salary TMS '
                    'Product Category'))
            if rec.employee_id.outsourcing is False:
                rec.expense_line_ids.create({
                    'name': _("Salary per travel: ") + str(travel.name),
                    'travel_id': travel.id,
                    'account_ids':product_id.property_account_expense_id.id,
                    'expense_id': rec.id,
                    'line_type': "salary",
                    'product_qty': 1.0,
                    'product_uom_id': product_id.uom_id.id,
                    'product_id': product_id.id,
                    'unit_price': rec.get_driver_salary(travel),
                    'control': True
                })
            

    @api.multi
    def create_diference_line(self, travel):
        
        for rec in self:
            for x in travel.cargo_id:
                print("-------------------------------------",x.name.id)
                if x.valor > x.advance_id.amount:
                    rec.expense_dif_ids.create({
                    'name': 'Diferencia del anticipo '+ str(x.advance_id.name),
                    'product_id':x.name.id,
                    'tipo':'reembolso',
                    'valor': x.valor - x.advance_id.amount,
                    'expense_id': rec.id
                    })
                if x.valor < x.advance_id.amount:
                    rec.expense_dif_ids.create({
                    'name': 'Diferencia del anticipo '+ str(x.advance_id.name),
                    'product_id':x.name.id,
                    'tipo':'sobrante',
                    'valor': x.advance_id.amount - x.valor,
                    'expense_id': rec.id
                    })
            
        for rec in self:
            rec.amount_refund = 0.0
            for line in rec.expense_line_ids:
                if line.line_type == 'refund':
                    rec.amount_refund += line.price_total
            # for line in rec.expense_dif_ids:
            #     if line.tipo == 'reembolso':
            #         rec.amount_refund += line.valor
            rec.amount_salary_discount = 0
            for line in rec.expense_line_ids:
                if line.line_type == 'salary_discount':
                    rec.amount_salary_discount += line.price_total
            # for line in rec.expense_dif_ids:
            #     if line.tipo != 'reembolso':
            #         rec.amount_salary_discount += (line.valor * -1)



    @api.multi
    def calculate_discounts(self, methods, loan):
        if loan.discount_type == 'fixed':
            total = loan.fixed_discount
        elif loan.discount_type == 'percent':
            total = loan.amount * (
                loan.percent_discount / 100)
        for key, value in methods.items():
            if loan.discount_method == key:
                if loan.expense_ids:
                    dates = []
                    for loan_date in loan.expense_ids:
                        dates.append(loan_date.date)
                    dates.sort(reverse=True)
                    end_date = datetime.strptime(
                        dates[0], "%Y-%m-%d")
                else:
                    end_date = datetime.strptime(
                        loan.date_confirmed, "%Y-%m-%d")
                start_date = datetime.strptime(
                    self.date, "%Y-%m-%d")
                total_date = start_date - end_date
                total_payment = total_date / value
                if int(total_payment.days) >= 1:
                    total_discount = (
                        total_payment.days * total)
            elif loan.discount_method == 'each':
                total_discount = total
        return total_discount

    @api.multi
    def get_expense_loan(self):
        loans = self.env['tms.expense.loan'].search([
            ('employee_id', '=', self.employee_id.id),
            ('balance', '>', 0.0)])
        methods = {
            'monthly': 30,
            'fortnightly': 15,
            'weekly': 7,
        }
        for loan in loans:
            total_discount = 0.0
            payment = loan.payment_move_id.id
            ac_loan = loan.active_loan
            if loan.lock != True and loan.state == 'confirmed' and ac_loan == True and payment and loan.balance > 0.0:
                if ac_loan:
                    loan.write({
                        'expense_id': self.id
                        })
                    total_discount = self.calculate_discounts(methods, loan)
                    total_final = loan.balance - total_discount
                    if total_final <= 0.0:
                        total_discount = loan.balance
                        #loan.write({'state': 'closed'})
                    expense_line = self.expense_line_ids.create({
                        'name': _("Loan: ") + str(loan.name),
                        'expense_id': self.id,
                        'line_type': "loan",
                        'account_ids': self.employee_id.tms_loan_account_id.id,
                        'product_id': loan.product_id.id,
                        'product_qty': 1.0,
                        'unit_price': total_discount,
                        'date': self.date,
                        'control': True
                    })
                    loan.expense_ids += expense_line
        for loan in loans:
            payment = loan.payment_move_id.id
            if loan.lock == True and loan.state == 'confirmed' and ac_loan == True and payment and loan.balance > 0.0:
                if loan.balance > 0.0:
                    loan.write({
                        'expense_id': self.id
                    })

                    descuento = 0

                    if loan.amount_discount > loan.balance:
                        descuento = loan.balance

                    if loan.amount_discount <= loan.balance:
                        descuento = loan.amount_discount

                    expense_line = self.expense_line_ids.create({
                        'name': _("Loan: ") + str(loan.name),
                        'expense_id': self.id,
                        'line_type': "loan",
                        'account_ids': self.employee_id.tms_loan_account_id.id,
                        'product_id': loan.product_id.id,
                        'product_qty': 1.0,
                        'unit_price': descuento,
                        'date': self.date,
                        'control': True
                    })

                    loan.expense_ids += expense_line


    @api.multi
    def get_travel_info(self):
        for rec in self:
            # Unattaching info from expense
            rec.unattach_info()
            # Finish unattach info from expense
            rec.get_expense_loan()
            
            for travel in rec.travel_ids:
                travel.write({'state': 'closed', 'expense_id': rec.id})
                for advance in travel.advance_ids:
                    # Creating advance lines
                    rec.create_advance_line(advance, travel)
                    # Finish creating advance lines
                for fuel_log in travel.fuel_log_ids:
                    # Creating fuel lines
                    rec.create_fuel_line(fuel_log, travel)
                    # Finish creating fuel lines
                # Creating salary lines
                rec.create_salary_line(travel)
                # Finish creating salary lines
                #creando diferencias
                #rec.create_diference_line(travel)


                for x in travel.advance_ids:
                    if x.to_expense == True:
                        rec.expense_dif_ids.create({
                            'name': 'Anticipo '+ str(x.name)+ " por "+str(x.product_id.name),
                            'product_id':x.product_id.id,
                            'tipo':'sobrante',
                            'valor': x.amount,
                            'expense_id': rec.id
                            })
                for x in travel.cargo_id:
                    if x.state == 'aprobado':
                        rec.expense_dif_ids.create({
                            'name': 'Gastos real '+ str(x.name.name),
                            'product_id':x.name.product_id.id,
                            'tipo':'reembolso',
                            'valor': x.valor,
                            'expense_id': rec.id
                            })


                # for x in travel.cargo_id:
                #     if x.valor > x.advance_id.amount:
                #         rec.expense_dif_ids.create({
                #         'name': 'Diferencia del anticipo '+ str(x.advance_id.name),
                #         'tipo':'reembolso',
                #         'valor': x.valor - x.advance_id.amount,
                #         'expense_id': rec.id
                #         })
                #     if x.valor < x.advance_id.amount:
                #         rec.expense_dif_ids.create({
                #         'name': 'Diferencia del anticipo '+ str(x.advance_id.name),
                #         'tipo':'sobrante',
                #         'valor': x.advance_id.amount - x.valor,
                #         'expense_id': rec.id
                #         })
            # a = 0
            # for x in rec.fuel_log_ids:
            #     a += x.price_total
            # b = 0
            # for x in rec.fuel_dif_ids:
            #     b += x.importe
            # if a > b:
            #     rec.expense_dif_ids.create({
            #         'name': 'Diferencia del combustible',
            #         'tipo':'sobrante',
            #         'valor': a-b,
            #         'expense_id': rec.id
            #         })
            # else:
            #     rec.expense_dif_ids.create({
            #         'name': 'Diferencia del combustible',
            #         'tipo':'reembolso',
            #         'valor': b-a,
            #         'expense_id': rec.id
            #         })

            # rec.amount_refund = 0.0
            # for line in rec.expense_line_ids:
            #     if line.line_type == 'refund':
            #         rec.amount_refund += line.price_total
            # for line in rec.expense_dif_ids:
            #     if line.tipo == 'reembolso':
            #         rec.amount_refund += line.valor
            # rec.amount_salary_discount = 0
            # for line in rec.expense_line_ids:
            #     if line.line_type == 'salary_discount':
            #         rec.amount_salary_discount += line.price_total
            # for line in rec.expense_dif_ids:
            #     if line.tipo != 'reembolso':
            #         rec.amount_salary_discount += (line.valor * -1)
            if rec.amount_percepciones > 0:
                
                for d in rec.employee_salary_ids:
                    product_id = self.env['product.product'].search([
                    ('name', '=', d.product_id.name)],limit=1)
                    print("vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv",d.product_id.id)
                    rec.expense_line_ids.create({
                        'name': _("Salario por percepciones ") + str(xx.name),
                        'expense_id': rec.id,
                        'account_ids': product_id.property_account_expense_id.id,
                        'line_type': "salary",
                        'product_qty': 1.0,
                        'product_uom_id': product_id.uom_id.id,
                        'product_id': product_id.id,
                        'unit_price': d.monto,
                        'control': True
                    })
            if rec.amount_deducciones > 0:
                line ="salary_discount"
                for xx in rec.employee_salary_ids:

                    productd_id = self.env['product.product'].search([
                    ('name', '=', xx.product_id.name)],limit=1)   
                    print("dddddddddddddd", productd_id.property_account_expense_id.id)
                    print ("////////////////////////////////////////////////////////////",productd_id.name ,self.employee_id.tms_loan_account_id.id)

                    if productd_id.name == 'INFONAVIT':  
                        rec.expense_line_ids.create({
                        'name': _("Descuento por deducciones ") + str(xx.name),
                        'expense_id': rec.id,
                        'account_ids': self.employee_id.tms_loan_account_id.id,
                        'line_type': line,
                        'product_qty': 1.0,
                        'product_uom_id': productd_id.uom_id.id,
                        'product_id': productd_id.id,
                        'unit_price': xx.monto,
                        'control': True
                        })
                    if productd_id.name == 'SALDO PENDIENTE':  
                        saldo_pendiente=rec.expense_line_ids.create({
                        'name': _("Descuento por deducciones ") + str(xx.name),
                        'expense_id': rec.id,
                        'account_ids': self.employee_id.tms_loan_account_id.id,
                        'line_type': line,
                        'product_qty': 1.0,
                        'product_uom_id': productd_id.uom_id.id,
                        'product_id': productd_id.id,
                        'unit_price': xx.monto,
                        'control': True
                        })
                        if saldo_pendiente:                            
                            for ll in saldo_pendiente:
                                if not ll.account_ids:
                                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!11")
                                    ll.write({
                                        'account_ids': self.employee_id.tms_loan_account_id.id,                                        
                                    })
                    if productd_id.name == 'Merma':  
                        rec.expense_line_ids.create({
                        'name': _("Descuento por deducciones ") + str(xx.name),
                        'expense_id': rec.id,
                        'account_ids': self.employee_id.tms_loan_account_id.id,
                        'line_type': line,
                        'product_qty': 1.0,
                        'product_uom_id': productd_id.uom_id.id,
                        'product_id': productd_id.id,
                        'unit_price': xx.monto,
                        'control': True
                        })
                    if productd_id.name != 'Merma' and productd_id.name != 'SALDO PENDIENTE' and productd_id.name != 'INFONAVIT':
                        print("++++++++++++++++++++++++++++++++",xx.name)
                        liquidacion=rec.expense_line_ids.create({
                        'name': _("Descuento por deducciones  ") + str(xx.name),
                        'expense_id': rec.id,
                        'account_ids': productd_id.property_account_expense_id.id,
                        'line_type': line,
                        'product_qty': 1.0,
                        'product_uom_id': productd_id.uom_id.id,
                        'product_id': productd_id.id,
                        'unit_price': xx.monto,
                        'control': True
                        })
                        if liquidacion:
                            for l in liquidacion:
                                if not l.line_type:
                                    l.write({
                                        'line_type': "salary_discount",                                        
                                    })


                       
               

            # diferencia_reem = 0
            # diferencia_cam = 0
            # cuenta_reembolso = False
            # cuenta_sobrante = False
            # for x in rec.expense_dif_ids:
            #     if x.tipo == 'reembolso':
            #         diferencia_reem += x.valor
            #         cuenta_reembolso = x.account_ids.id
            #     if x.tipo == 'sobrante':
            #         diferencia_cam += x.valor
            #         cuenta_sobrante = x.account_ids.id
            for r in rec.expense_dif_ids:
                if r.tipo == "reembolso":
                    product_id = self.env['product.product'].search([
                    ('name', '=', r.product_id.name)],limit=1)
                    print("cccccccccccccccccccccccccccccccccccccccccccccccc",product_id)
                    rec.expense_line_ids.create({
                        'name': _("Reembolso por diferencia de gastos ") + str(r.name),
                        'expense_id': rec.id,
                        'account_ids': product_id.property_account_expense_id.id,
                        'line_type': "salary",
                        'product_qty': 1.0,
                        'product_uom_id': product_id.uom_id.id,
                        'product_id': product_id.id,
                        'unit_price': -r.valor,
                        'control': True
                    })
                else:
                    productd_ids = self.env['product.product'].search([
                    ('name', '=', r.product_id.name)],limit=1)
                    rec.expense_line_ids.create({
                        'name': _("Descuento por diferencia de gastos ") + str(r.name),
                        'expense_id': rec.id,
                        'account_ids': self.employee_id.tms_loan_account_id.id,
                        'line_type': "salary_discount",
                        'product_qty': 1.0,
                        'product_uom_id': productd_ids.uom_id.id,
                        'product_id': productd_ids.id,
                        'unit_price': r.valor,
                        'control': True
                    })

    @api.depends('travel_ids')
    def get_driver_salary(self, travel):
        for rec in self:
            driver_salary = 0.0
            for factor in travel.driver_factor_ids:
                driver_salary += factor.total
            #     income = 0.0
            #     for line in waybill.waybill_line_ids:
            #         if line.product_id.apply_for_salary:
            #             income += line.price_subtotal
            #     if waybill.currency_id.name == 'USD':
            #         income = (income *
            #                   self.env.user.company_id.expense_currency_rate)
            #     if waybill.driver_factor_ids:
            #         for factor in waybill.driver_factor_ids:
            #             driver_salary += factor.get_amount(
            #                 weight=waybill.product_weight,
            #                 distance=waybill.distance_route,
            #                 distance_real=waybill.distance_real,
            #                 qty=waybill.product_qty,
            #                 volume=waybill.product_volume,
            #                 income=income,
            #                 employee=rec.employee_id)
            #     elif travel.driver_factor_ids:
            #         for factor in travel.driver_factor_ids:
            #             driver_salary += factor.get_amount(
            #                 weight=waybill.product_weight,
            #                 distance=waybill.distance_route,
            #                 distance_real=waybill.distance_real,
            #                 qty=waybill.product_qty,
            #                 volume=waybill.product_volume,
            #                 income=income,
            #                 employee=rec.employee_id)
            #     else:
            #         raise ValidationError(_(
            #             'Oops! You have not defined a Driver factor in '
            #             'the Travel or the Waybill\nTravel: %s' %
            #             travel.name))
            return driver_salary

    


    @api.multi
    def create_supplier_invoice(self, line):
        journal_id = self.operating_unit_id.expense_journal_id.id
        product_account = (
            line.product_id.product_tmpl_id.property_account_expense_id.id)
        if not product_account:
            product_account = (
                line.product_id.categ_id.property_account_expense_categ_id.id)
        if not product_account:
            raise ValidationError(
                _('Error !'),
                _('There is no expense account defined for this'
                    ' product: "%s") % (line.product_id.name'))
        if not journal_id:
            raise ValidationError(
                _('Error !',
                    'You have not defined Travel Expense Supplier Journal...'))
        invoice_line = (0, 0, {
            'name': _('%s (TMS Expense Record %s)') % (line.product_id.name,
                                                       line.expense_id.name),
            'origin': line.expense_id.name,
            'account_id': line.account_ids.id,
            'quantity': line.product_qty,
            'price_unit': line.unit_price,
            'invoice_line_tax_ids':
            [(6, 0,
                [x.id for x in line.tax_ids])],
            'uom_id': line.product_uom_id.id,
            'product_id': line.product_id.id,
        })
        notes = line.expense_id.name + ' - ' + line.product_id.name
        partner_account = line.partner_id.property_account_payable_id.id
        invoice = {
            'origin': line.expense_id.name,
            'type': 'in_invoice',
            'journal_id': journal_id,
            'reference': line.invoice_number,
            'account_id': partner_account,
            'partner_id': line.partner_id.id,
            'invoice_line_ids': [invoice_line],
            'currency_id': line.expense_id.currency_id.id,
            'payment_term_id': (
                line.partner_id.property_supplier_payment_term_id.id
                if
                line.partner_id.property_supplier_payment_term_id
                else False),
            'fiscal_position_id': (
                line.partner_id.property_account_position_id.id or False),
            'comment': notes,
            'operating_unit_id': line.expense_id.operating_unit_id.id,
        }
        invoice_id = self.env['account.invoice'].create(invoice)
        line.invoice_id = invoice_id
        return invoice_id

    @api.multi
    def reconcile_supplier_invoices(self, invoice_ids, move_id):
        move_line_obj = self.env['account.move.line']
        for invoice in invoice_ids:
            move_ids = []
            invoice_str_id = str(invoice.id)
            expense_move_line = move_line_obj.search(
                [('move_id', '=', move_id.id), (
                    'name', 'ilike', invoice_str_id)])
            if not expense_move_line:
                raise ValidationError(
                    _('Error ! Move line was not found,'
                        ' please check your data.'))
            move_ids.append(expense_move_line.id)
            invoice_move_line_id = invoice.move_id.line_ids.filtered(
                lambda x: x.account_id.reconcile)
            move_ids.append(invoice_move_line_id.id)
            reconcile_ids = move_line_obj.browse(move_ids)
            reconcile_ids.reconcile()
        return True

    @api.onchange('operating_unit_id', 'unit_id')
    def _onchange_operating_unit_id(self):
        travels = self.env['tms.travel'].search([
            ('operating_unit_id', '=', self.operating_unit_id.id),
            ('state', '=', 'done'),
            ('unit_id', '=', self.unit_id.id)])
        employee_ids = travels.mapped('employee_id').ids
        if self.employee_id.id not in employee_ids:
            self.employee_id = False
        tlines_units = self.travel_ids.mapped('unit_id').ids
        tlines_drivers = self.travel_ids.mapped('employee_id').ids
        if (self.unit_id.id not in tlines_units and
                self.employee_id.id not in tlines_drivers):
            self.travel_ids = False
        return {
            'domain': {
                'employee_id': [
                    ('id', 'in', employee_ids), ('driver', '=', True)],
            }
        }

    @api.onchange('unit_id')
    def onchange_employee_id(self):
        self.employee_id = self.unit_id.employee_id.id

    @api.multi
    def get_amount_total(self):
        for rec in self:
            amount_subtotal = 0.0
            for line in rec.expense_line_ids:
                if line.line_type in ['real_expense', 'fuel', 'fuel_cash']:
                    amount_subtotal += line.price_subtotal
            return amount_subtotal

    @api.multi
    def get_amount_tax(self):
        for rec in self:
            tax_amount = 0.0
            for line in rec.expense_line_ids:
                if line.line_type in ['real_expense', 'fuel', 'fuel_cash']:
                    tax_amount += line.tax_amount
            return tax_amount

    @api.multi
    def get_value(self, type_line):
        for rec in self:
            value = 0.0
            for line in rec.expense_line_ids:
                if line.line_type == type_line:
                    value += line.price_total
        return value


    @api.multi
    def get_test(self):
        for rec in self:
            DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            # week_day = today.weekday()
            # month = int(rec.date[5:7])
            # month_day = int(rec.date[8:10])
            f_i = datetime.strptime(rec.start_date, DATETIME_FORMAT)
            f_f = datetime.strptime(rec.end_date, DATETIME_FORMAT)
            v = 0
            q = 0
            m = 0
            while f_i <= f_f:
                if f_i.weekday() == 4:
                    v += 1
                if int(f_i.strftime("%d")) == 30:
                    m += 1
                if int(f_i.strftime("%d")) == 15 or int(f_i.strftime("%d")) == 30:
                    q += 1
                f_i += timedelta(days=1)
            print("Semanas: "+str(v))
            print("Quincenas: "+str(q))
            print("Mensualidades: "+str(m))
