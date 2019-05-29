# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class tms_operat_ih(models.Model):
# 	_inherit = 'tms.event.category'
# 	travel_id=fields.Many2one('tms.event.category', string='table')

class tms_categories_events(models.Model):


	_name = 'tms.event.category'

	name=fields.Char(string='Nombre')
	gps_code=fields.Char(string='GPS Code ')
	parent_id=fields.Many2one('tms.event.category',string='Campo a actualizar')
	company_id=fields.Many2one('res.company',string='Compañia')
	active= fields.Boolean(string='Activo')
	gps_type= fields.Selection(selection=[('in', 'Recibido del GPS'),('out', 'Enviar al GPS'),('none', 'None') ],string='GPS Tipo',default='none')
	action_ids = fields.Many2many(
        'tms.event.action',
        string='Travels')
	notes=fields.Text(string='Notas')
