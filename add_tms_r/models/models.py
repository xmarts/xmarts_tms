# -*- coding: utf-8 -*-

from odoo import models, fields, api


class fleet_vehicle_red_tape(models.Model):
	_name = 'add_tms.add_tms'

	red_tape_id=fields.Many2one('fleet.vehicle.red_tape_type', string='Trámite Vehicular', required=True)
	vehicle_id = fields.Many2one('fleet.vehicle',string='Vehículo', required=True)
	vehicle_type_id = fields.Many2one('fleet.vehicle.category',string='Tipo de Vehículo')
	date = fields.Date(string='Fecha')
	partner_id = fields.Many2one('fleet.vehicle.red_tape',string='Empresa')
	name= fields.Char(string="Descripcíon")
	date_start = fields.Date(string='Fecha Inicio')
	amount = fields.Float(string='Importe')
	date_end = fields.Date(string='Fecha Fin')
	amount_paid = fields.Float(string='Monto Pagado')
	notes =fields.Text(string='Descripcíon')
	 
	state = fields.Selection([
	('draft', 'Borrador'),
	('pending', 'Pendiente'),
	('progress', 'En Proceso'),
	('done', 'Realizado'),
	('cancel','Cancelado')
	],default='draft')




class add_tms_advances(models.Model):
	_inherit= 'tms.advance'

	
	vehicle_id = fields.Many2one('fleet.vehicle',string='Unidad Motiriz')
	product_uom_qty= fields.Float(string='Cantidad')
	price_unit = fields.Float(string='Precio Unitario') #corregir related='product_id.price_unit' 
	subtotal = fields.Float(string='Subtotal',compute='_compute_produc_qty')
	total = fields.Float(string='Total', compute='_compute_produc_total')
	currency_id = fields.Many2one('res.currency',string='Moneda')

	@api.onchange('product_id','product_tmpl_id')
	@api.depends('product_id','product_tmpl_id')
	def _onchange_country_id(self):
		self.price_unit = self.product_id.product_tmpl_id.standard_price
	
	# @api.onchange('product_id')
	# def _onchange_contry_id(self):
	# 	self.price_unit = self.product_id.weight

	@api.one
	@api.depends('product_uom_qty', 'price_unit')
	def _compute_produc_qty(self):
		self.subtotal = self.product_uom_qty * self.price_unit
		return True

	@api.one
	@api.depends('amount', 'subtotal')
	def _compute_produc_total(self):
		self.total = self.amount + self.subtotal
		return True

	# @api.model
	# def create(self):
	# 	impuesto=0
	# for x in self.product_id.product_tmpl_id.supplier_taxes_id:
	# 	impuesto = impuesto + ((self.coste / 100) *  (x.amount))
	# 	if x.amount == 0:
	# 		vals['amount'] = impuesto




# class add_tms_travel(models.Model): revisar !!!!!!!!!!!!!!!!!!
# 	 _inherit= 'tms.travel'

# 	 expense_id=fields.Many2one('tms.expense', string='Liquidacíon')
# 	 expense2_id=fields.Many2one('tms.expense',string='Liquidacíon para 2do Operador')


	 
