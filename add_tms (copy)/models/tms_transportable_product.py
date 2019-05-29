# -*- coding: utf-8 -*-

from odoo import models, fields, api


class tms_categories_events(models.Model):


	_name = 'tms.waybill.transportable'
	_inherit =['mail.thread']
	name=fields.Char(string='Nombre')
	product_uom=fields.Many2one('product.uom',string='UdM x Defecto')
	notes=fields.Text(string='Notas')