# -*- coding: utf-8 -*-

from odoo import models, fields, api

class tms_tires_lado(models.Model):
	_name='tms.tires.lado'
	name=fields.Char(string='Nombre')

class tms_tires_campos(models.Model):
	_name = 'tms.tires.campos'

	
	profu_ultimo=fields.Char(string='Ultimo')	
	profu_inicial=fields.Char(string='Inicial')
	posi_lado=fields.Many2one('tms.tires.lado',string='Lado')	
	posi_estandar=fields.Float(string='Estandar (mm)')
	nueva_med_condicion=fields.Selection(selection=[('bien', 'Bien'),('regular', 'Regular'),('malo', 'Malo')],string='Condición',default='bien')
	
	nueva_med_presion=fields.Float(string='Presión (lbs)')
	nueva_med_profundidad=fields.Float(string='Profundidad (mm)')

class tms_tires(models.Model):
	_name = 'tms.tires'

	date= fields.Datetime(string='Fecha Creación')
	vehicle=fields.Many2one('fleet.vehicle',string='Vehiculo')
	waybill_ids = fields.One2many('tms.tires.campos', 'profu_ultimo', string='Advances')
	