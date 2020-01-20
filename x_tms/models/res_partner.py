# -*- coding: utf-8 -*-
from odoo import fields, models

class ResPartner(models.Model):
	_inherit = 'res.partner'

	merma_permitida_por = fields.Float(string="Merma permitida", default=0)
	merma_permitida_kg = fields.Float(string="Merma permitida kilogramos", default=0)