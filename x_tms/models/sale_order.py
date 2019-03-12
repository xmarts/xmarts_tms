# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class SaleOrder(models.Model):
	_inherit = "sale.order"

	tarifa_cliente = fields.Float(string='Tarifa cliente', default=0,required=True)
	product = fields.Many2one("product.template", string="Producto a transportar",required=True)
	ruta = fields.Many2one("tms.route", string="Ruta a tomar",required=True)