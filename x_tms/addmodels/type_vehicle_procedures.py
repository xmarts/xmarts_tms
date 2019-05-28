# -*- coding: utf-8 -*-

from odoo import models, fields, api

class tms_vehicle_red_tape_type(models.Model):
	_name='fleet.vehicle.red_tape_type'
	_inherit =['mail.thread']

	name=fields.Char(string='Nombre')
	parent_id=fields.Many2one('fleet.vehicle.red_tape_type',string='Padre')
	tipo= fields.Selection(selection=[('view', 'Ver'),('normal', 'Normal') ],string='Tipo',default='view')
	notes=fields.Text(string='Notas')
	active = fields.Boolean(string='Outsourcing?')
