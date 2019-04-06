# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models


class SaleOrder(models.Model):
	_inherit = "sale.order"

	tarifa_cliente = fields.Float(string='Tarifa cliente', default=0,required=True)
	product = fields.Many2one("product.template", string="Producto a transportar",required=True)
	ruta = fields.Many2one("tms.route", string="Ruta 1 a tomar",required=True)
	ruta2 = fields.Many2one("tms.route", string="Ruta 2 a tomar")



	@api.depends('order_line')
	@api.onchange('ruta')
	def _onchange_ruta_pedido(self):
		# product_caseta_obj = self.env['product.product'].search([('es_caseta','=',True)], limit=1)
		product_factor_obj = self.env['product.product'].search([('es_factor_op','=',True)], limit=1)
		product_combustible_obj = self.env['product.product'].search([('es_combustible','=',True)], limit=1)
		line_ids = []
		res = {'value':{
                'order_line':[],
            }
		}
		# sum_casetas = 0
		# for sca in self.ruta.tollstation_ids:
		# 	sum_casetas += sca.costo_caseta
		# lineca = {
  #         'product_id': product_caseta_obj.id,
		#   'product_uom': product_caseta_obj.uom_id.id,
		#   'name': 'Costo de las casetas generado en la ruta',
		#   'price_unit': sum_casetas,
		#   'product_uom_qty':1
  #       }
		sum_factor = 0
		for sca in self.ruta.driver_factor_ids:
			sum_factor += sca.fixed_amount
		linefa = {
          'product_id': product_factor_obj.id,
		  'product_uom': product_factor_obj.uom_id.id,
		  'name': 'Costo del operador generado en la ruta',
		  'price_unit': sum_factor,
		  'product_uom_qty':1
        }
		# sum_combustible = 0
		# for sca in self.ruta.fuel_efficiency_ids:
		# 	sum_combustible += sca.performance
		# lineco = {
  #         'product_id': product_combustible_obj.id,
		#   'product_uom': product_combustible_obj.uom_id.id,
		#   'name': 'Costo del combustible generado en la ruta',
		#   'price_unit': sum_combustible,
		#   'product_uom_qty':1
  #       }
		# line_ids += [lineca]
		line_ids += [linefa]
		# line_ids += [lineco]
		res['value'].update({
            'order_line': line_ids,
		})
		return res
