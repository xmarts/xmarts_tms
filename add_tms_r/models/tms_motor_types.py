# -*- coding: utf-8 -*-

from odoo import models, fields, api


class fleet_vehicle_motor(models.Model):


	_name = 'fleet.vehicle.motor'
	name=fields.Char(string='Nombre')
	parent_id=fields.Many2one('fleet.vehicle.motor', string='Padre')
	engine_performance_drive_unit=fields.Float(string='Redimiento Unidad Motriz')
	engine_performance_1trailer=fields.Float(string='Redimiento 1 Remolque')
	engine_performance_2trailer=fields.Float(string='Redimiento 2 Remolque')
	tipo= fields.Selection(selection=[('view', 'Ver'),('normal', 'Normal')],string='Tipo',default='view')
	notes=fields.Text(string='Notas')
