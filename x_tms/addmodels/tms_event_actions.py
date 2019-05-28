# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class tms_operat_ih(models.Model):
# 	_inherit = 'tms.event.category'
# 	parent_id=fields.Many2one('tms.event.category', string='table')

class tms_event_Actions(models.Model):
	_name = 'tms.event.action'
	_inherit =['mail.thread']

	name=fields.Char(string='Nombre')
	field_id=fields.Many2one('ir.model.fields',string='Campo a actualizar')
	object_id=fields.Many2one('ir.model',string='Objeto')
	active= fields.Boolean(string='Activo')
	notes=fields.Text(string='Notas')
	get_value=fields.Text(string='value')
	# event_category_ids = fields.One2many('tms.event.category', 'parent_id', string='Advances')