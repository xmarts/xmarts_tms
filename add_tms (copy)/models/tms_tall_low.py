# -*- coding: utf-8 -*-

from odoo import models, fields, api


class fleet_vehicle_status_reason_data(models.Model):
	_name = 'fleet.vehicle.status_reason.data'
	_inherit =['mail.thread']

	date= fields.Datetime(string='Fecha')
	vehicle_id= fields.Many2one( 'fleet.vehicle',string='Vehículo')
	prev_state= fields.Selection(selection=[('active', 'Activo'),('inactive', 'Inactivo')],string='Estado Previo',default='active')
	state_cause_id= fields.Many2one( 'fleet.vehicle.status_reason',string='Razón de Estado')
	name =fields.Char(string='Descripción')
	vehicle_type_id=fields.Many2one('fleet.vehicle.category', string='Tipo de Vehículo')
	new_state= fields.Selection(selection=[('active', 'Activo'),('inactive', 'Inactivo')],string='Nuevo estado',default='active')
	notes=fields.Text(string='Notas')		
	