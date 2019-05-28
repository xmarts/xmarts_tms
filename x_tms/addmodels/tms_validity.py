# -*- coding: utf-8 -*-

from odoo import models, fields, api


class fleet_vehicle_validity(models.Model):
	_name = 'fleet.vehicle.validity'
	_inherit =['mail.thread']

	name=fields.Char(string='Nombre')
	parent_id=fields.Many2one('fleet.vehicle.validity', string='Padre')
	tipo= fields.Selection(selection=[('view', 'Ver'),('normal', 'Normal')],string='Tipo',default='view')
	mandatory=fields.Boolean(string='Obligatorio')
	notes=fields.Text(string='Notas')


