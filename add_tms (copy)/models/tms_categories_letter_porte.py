# -*- coding: utf-8 -*-

from odoo import models, fields, api



class tms_waybill_category(models.Model):


	_name = 'tms.waybill.category'
	_inherit =['mail.thread']

	name=fields.Char(string='Categoria')
	operating_unit_id=fields.Many2one('operating.unit',string='Unidad Operativa')
	active=fields.Boolean(string='Activo')
	Descripcion=fields.Text(string='Descripción')