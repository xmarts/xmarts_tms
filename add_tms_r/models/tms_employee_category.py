# -*- coding: utf-8 -*-

from odoo import models, fields, api

class tms_categories_events(models.Model):


	_name = 'hr.employee.category'
	name = fields.Char('Etiqueta del empleado')