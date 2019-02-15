# -*- coding: utf-8 -*-

from odoo import models, fields, api


class fleet_vehicle_category(models.Model):
	_name = 'fleet.vehicle.category'

	name=fields.Char(string='Nombre')
	parent_id=fields.Many2one('fleet.vehicle.category', string='Padre')
	tipo= fields.Selection(selection=[('view', 'Ver'),('normal', 'Normal')],string='Tipo',default='view')
	notes=fields.Text(string='Notas')
	