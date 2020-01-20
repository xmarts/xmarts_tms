# -*- coding: utf-8 -*-

from odoo import models, fields, api


class fleet_vehicle_red_tape(models.Model):
	_name = 'fleet.vehicle.red_tape'

	#red_tape_id=fields.Many2one('fleet.vehicle.red_tape_type', string='Trámite Vehicular', required=True)
	name=fields.Char(string="Nombre")
	numero=fields.Char(string="Numero de Tramite")
	vehicle_id = fields.Many2one('fleet.vehicle',string='Vehículo', required=True)
	vehicle_type_id = fields.Many2one('fleet.vehicle.category',string='Tipo de Vehículo')
	date = fields.Date(string='Fecha')
	partner_id = fields.Many2one('res.partner',string='Empresa')
	descripcion= fields.Char(string="Descripcíon")
	date_start = fields.Date(string='Fecha Inicio')
	amount = fields.Float(string='Importe')
	date_end = fields.Date(string='Fecha Fin')
	amount_paid = fields.Float(string='Monto Pagado')
	notes =fields.Text(string='Descripcíon')
	adjunto = fields.Binary(string="Adjunto")
	prorroga=fields.Boolean(string='Prorroga')
	dias=fields.Char(string='Dias')
	#state = fields.Selection([
	#('draft', 'Borrador'),
	#('pending', 'Pendiente'),
	#('progress', 'En Proceso'),
	#('done', 'Realizado'),
	#('cancel','Cancelado')
	#],default='draft')