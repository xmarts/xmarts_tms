# -*- coding: utf-8 -*-

from odoo import models, fields, api

#class tms_operat_ih(models.Model):
#	_inherit = 'fleet.vehicle.odometer'
#	travel_id=fields.Many2one('tms.advance', string='table')

class fleet_vehicle_odometer_device(models.Model):


	_name = 'fleet.vehicle.odometer.device'
	_inherit =['mail.thread']

	name=fields.Char(string='Nombre')
	vehicle_id=fields.Many2one('fleet.vehicle',string='Vehículo')
	date_start=fields.Datetime(string='Fecha Inicio')
	odometer_start= fields.Float(string='Conteo Inicial')
	date=fields.Datetime(string='Fecha')	
	date_end=fields.Datetime(string='Fecha Fin')
	odometer_end= fields.Float(string='Conteo Final')
	
	notes=fields.Text(string='Notas')

	# state = fields.Selection([
	# ('draft', 'Borrador'),
	# ('active', 'Activo'),
	# ('inactive', 'Inactivo')

	# ],default='draft')
