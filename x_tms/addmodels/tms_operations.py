# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class tms_operat_ih(models.Model):
# 	_inherit = 'tms.advance'
# 	travel_id=fields.Many2one('tms.advance', string='table')

#class tms_operat_fuelvoucher(models.Model):
#	_inherit = 'fleet.vehicle.log.fuel'
#	purchaser_id=fields.Many2one('fleet.vehicle.log.fuel', string='table_dos')

#class tms_operat_fuelvoucher(models.Model):
#	_inherit = 'tms.waybill'
#	partner_id=fields.Many2one('tms.waybill', string='table_tres')

class tms_operat_expense(models.Model):
	_inherit = 'tms.expense.line'
	operation_id    = fields.Many2one('tms_operat.tms_operat', string='Operation', ondelete='restrict', required=False, readonly=False,
                                     domain=[('state', 'in', ('process','done'))])


class tms_operat(models.Model):
	_name = 'tms_operat.tms_operat'


	name = fields.Char(string='Operacíon', requiered=True)
	date=fields.Date(string='Fecha')
	date_star=fields.Datetime(string='Fecha de Inicio')
	partner_id=fields.Many2one('res.partner', string='Cliente')
	date_end=fields.Datetime(string='Fecha Finalización')
	advance_ids = fields.One2many('tms.advance', 'travel_id', string='Advances')
	fuelvoucher_ids = fields.One2many('tms.advance', 'travel_id', string='Advances')
	waybill_ids = fields.One2many('tms.waybill', 'partner_id', string='Advances')
	#expense_line_ids = fields.One2many('fleet.vehicle.log.fuel', 'purchaser_id', string='Advances')
	expense_line_ids = fields.One2many('tms.expense.line', 'operation_id', string='Travel Expense Lines', readonly=True)


	state = fields.Selection([
	('draft', 'Borrador'),
	('progress', 'En Proceso'),
	('done', 'Realizado')

	],default='draft')