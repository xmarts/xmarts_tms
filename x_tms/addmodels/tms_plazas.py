# -*- coding: utf-8 -*-

from odoo import models, fields, api


class fleet_vehicle_motor(models.Model):


	_name = 'tms.place'
	name=fields.Char(string='Plazas', requiered=True)
	state_id=fields.Many2one('res.country.state',string='Estado')
	latitude=fields.Float(string='latitud')
	country_id=fields.Many2one('res.country',string='Pais')
	longitude=fields.Float(string='Longitud')