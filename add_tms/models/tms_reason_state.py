# -*- coding: utf-8 -*-

from odoo import models, fields, api


class fleet_vehicle_status_reason(models.Model):
	_name = 'fleet.vehicle.status_reason'
	_inherit =['mail.thread']

	name=fields.Char(string='Nombre')
	parent_id=fields.Many2one('fleet.vehicle.status_reason', string='Padre')
	tipo= fields.Selection(selection=[('view', 'Ver'),('normal', 'Normal')],string='Tipo',default='view')
	notes=fields.Text(string='Notas')
