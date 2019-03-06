# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class TmsRoutePlace(models.Model):
    _name = 'tms.route.place'
    _order = 'sequence'

    route_id = fields.Many2one(
        'tms.route',
        required=True,
        string="Route")
    sequence = fields.Integer(default=10)
    place_id = fields.Many2one('tms.place', string="Place")
    calle = fields.Char(string="Calle",readonly=True, related="place_id.calle")
    noexterior = fields.Char(string="No. Exterior",readonly=True, related="place_id.noexterior")
    nointerior = fields.Char(string="No. Interior",readonly=True, related="place_id.nointerior")
    localidad = fields.Many2one('res.colonia.zip.sat.code', string='Localidad',readonly=True, related="place_id.localidad")
    latitude = fields.Float(string="Latitud",readonly=True, related="place_id.latitude")
    longitude = fields.Float(string="Longitud",readonly=True, related="place_id.longitude")
