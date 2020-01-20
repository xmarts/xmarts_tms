# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
##############################################################################

import requests
import simplejson as json
from odoo import _, api, exceptions, fields, models
import base64
from suds.client import Client
from lxml import etree
from zeep import Client
from xml.etree import ElementTree as ET
import sys
import locale

class TmsRoute(models.Model):
    _name = 'tms.route'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Routes'

    name = fields.Char('Route Name', size=64, required=True, index=True)
    departure_id = fields.Many2one('tms.place', 'Departure', required=True)
    arrival_id = fields.Many2one('tms.place', 'Arrival', required=True)
    distance = fields.Float(
        'Distance (mi./kms)', digits=(14, 4),
        help='Route distance (mi./kms)', required=True)
    travel_time = fields.Float(
        'Travel Time (hrs)', digits=(14, 4),
        help='Route travel time (hours)')
    notes = fields.Text()
    active = fields.Boolean(default=True)
    driver_factor_ids = fields.One2many(
        'tms.factor', 'route_id',
        string="Expense driver factor")
    distance_loaded = fields.Float(
        string='Distance Loaded (mi./km)',
        required=True
    )
    distance_empty = fields.Float(
        string='Distance Empty (mi./km)',
        required=True
    )
    fuel_efficiency_ids = fields.One2many(
        'tms.route.fuelefficiency',
        'route_id',
        string="Fuel Efficiency")
    route_place_ids = fields.One2many(
        'tms.route.place',
        'route_id',
        string='Places')
    route_stop_ids = fields.One2many(
        'tms.route.stops',
        'route_id',
        string='Places')
    tollstation_ids = fields.Many2many(
        'tms.route.tollstation', string="Toll Station")
    note_ids = fields.One2many('tms.route.note', 'route_id', string='Notes')
    cargos_id = fields.One2many('tms.viaje.cargos', 'route_id', string="Cargos Adicionales")
    # total_casetas = fields.Float(string="Total Casetas", compute="get_t_casetas")

    # @api.multi
    # @api.depends('tollstation_ids', 'total_casetas')
    # def get_t_casetas(self):
    #     for record in self:
    #         suma = 0.0
    #         for rec in record.tollstation_ids:
    #             suma += rec.costo_caseta
    #         record.total_casetas = suma

    @api.depends('distance_empty', 'distance')
    @api.onchange('distance_empty')
    def on_change_disance_empty(self):
        for rec in self:
            if rec.distance_empty < 0.0:
                raise exceptions.ValidationError(
                    _("The value must be positive and lower than"
                        " the distance route."))
            rec.distance_loaded = rec.distance - rec.distance_empty

    @api.depends('distance_loaded', 'distance')
    @api.onchange('distance_loaded')
    def on_change_disance_loaded(self):
        for rec in self:
            if rec.distance_loaded < 0.0:
                raise exceptions.ValidationError(
                    _("The value must be positive and lower than"
                        " the distance route."))
            rec.distance_empty = rec.distance - rec.distance_loaded

    #ruta_file = fields.Binary('Archivo, detalles de ruta', readonly=True)

    mapa_link = fields.Char(string="Enlace de ruta")

    fuel_log_ids = fields.One2many(
        'fleet.vehicle.log.fuel.tem', 'route_id', string='Vales de combustible')

    @api.multi
    def get_route_soap(self):
        paradas = []
        it = 0
        for r in self.route_place_ids:
            paradas.append([r.place_id.name,r.place_id.latitude,r.place_id.longitude])
            it += 1
        it = 20 - it
        if it > 0:
            i = 0

            while it > i:
                paradas.append(["",0,0])
                i += 1

        client = Client('http://www.gmapserver.com/GlobalMap_API/V3/GlobalMapWSDL.wsdl')
        result = client.service.CalcularRuta("225217657648564", 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 3,
        str(self.departure_id.name), self.departure_id.latitude, self.departure_id.longitude, 0, 0,
        str(self.arrival_id.name), self.arrival_id.latitude, self.arrival_id.longitude, 0, 0,
        str(paradas[0][0] or ""), float(paradas[0][1] or 0), float(paradas[0][2] or 0), 0, 0, str(paradas[1][0] or ""), float(paradas[1][1] or 0), float(paradas[1][2] or 0), 0, 0,
        str(paradas[2][0] or ""), float(paradas[2][1] or 0), float(paradas[2][2] or 0), 0, 0, str(paradas[3][0] or ""), float(paradas[3][1] or 0), float(paradas[3][2] or 0), 0, 0,
        str(paradas[4][0] or ""), float(paradas[4][1] or 0), float(paradas[4][2] or 0), 0, 0, str(paradas[5][0] or ""), float(paradas[5][1] or 0), float(paradas[5][2] or 0), 0, 0,
        str(paradas[6][0] or ""), float(paradas[6][1] or 0), float(paradas[6][2] or 0), 0, 0, str(paradas[7][0] or ""), float(paradas[7][1] or 0), float(paradas[7][2] or 0), 0, 0,
        str(paradas[8][0] or ""), float(paradas[8][1] or 0), float(paradas[8][2] or 0), 0, 0, str(paradas[9][0] or ""), float(paradas[9][1] or 0), float(paradas[9][2] or 0), 0, 0,
        str(paradas[10][0] or ""), float(paradas[10][1] or 0), float(paradas[10][2] or 0), 0, 0, str(paradas[11][0] or ""), float(paradas[11][1] or 0), float(paradas[11][2] or 0), 0, 0,
        str(paradas[12][0] or ""), float(paradas[12][1] or 0), float(paradas[12][2] or 0), 0, 0, str(paradas[13][0] or ""), float(paradas[13][1] or 0), float(paradas[13][2] or 0), 0, 0,
        str(paradas[14][0] or ""), float(paradas[14][1] or 0), float(paradas[14][2] or 0), 0, 0, str(paradas[15][0] or ""), float(paradas[15][1] or 0), float(paradas[15][2] or 0), 0, 0,
        str(paradas[16][0] or ""), float(paradas[16][1] or 0), float(paradas[16][2] or 0), 0, 0, str(paradas[17][0] or ""), float(paradas[17][1] or 0), float(paradas[17][2] or 0), 0, 0,
        str(paradas[18][0] or ""), float(paradas[18][1] or 0), float(paradas[18][2] or 0), 0, 0, str(paradas[19][0] or ""), float(paradas[19][1] or 0), float(paradas[19][2] or 0), 0, 0,
        )
        result = result.encode('utf-8')
        tree = ET.XML(result)
        distancia = ""
        tiempo = ""
        for r in tree.findall("RESULTADOS/DISTANCIA_TOTAL"):
            distancia = r.text
            distancia = distancia[:-4]

        thora = ""
        tmin = ""
        for r in tree.findall("RESULTADOS/TIEMPO_TOTAL"):
            tiempo = r.text
            thora = tiempo[:-5]
            tmin = tiempo[4:6]

        for r in tree.findall("LINKS/MAPA"):
            self.mapa_link = r.text

        print(result)
        self.distance = float(distancia.replace(",",""))
        self.travel_time = (float(thora)+(float(tmin)/60))


    @api.multi
    def get_route_info(self, error=False):
        for rec in self:
            departure = {
                'latitude': rec.departure_id.latitude,
                'longitude': rec.departure_id.longitude
            }
            arrival = {
                'latitude': rec.arrival_id.latitude,
                'longitude': rec.arrival_id.longitude
            }
            if not departure['latitude'] and not departure['longitude']:
                raise exceptions.UserError(_(
                    "The departure don't have coordinates."))
            if not arrival['latitude'] and not arrival['longitude']:
                raise exceptions.UserError(_(
                    "The arrival don't have coordinates."))
            url = 'http://maps.googleapis.com/maps/api/distancematrix/json'
            origins = (str(departure['latitude']) + ',' +
                       str(departure['longitude']))
            destinations = ''
            places = [str(x.place_id.latitude) + ',' +
                      str(x.place_id.longitude) for x in rec.route_place_ids
                      if x.place_id.latitude and x.place_id.longitude]
            for place in places:
                origins += "|" + place
                destinations += place + "|"
            destinations += (str(arrival['latitude']) + ',' +
                             str(arrival['longitude']))
            params = {
                'origins': origins,
                'destinations': destinations,
                'mode': 'driving',
                'language': self.env.lang,
                'sensor': 'false',
            }
            try:
                result = json.loads(requests.get(url, params=params).content)
                distance = duration = 0.0
                if result['status'] == 'OK':
                    if rec.route_place_ids:
                        for row in result['rows']:
                            distance += (
                                row['elements'][0]['distance']
                                   ['value'] / 1000.0)
                            duration += (
                                row['elements'][0]['duration']
                                   ['value'] / 3600.0)
                self.distance = distance
                self.travel_time = duration
            except Exception:
                raise exceptions.UserError(_("Google Maps is not available."))

    @api.multi
    def open_in_google(self):
        for route in self:
            points = (
                str(route.departure_id.latitude) + ',' +
                str(route.departure_id.longitude) +
                (',' if route.route_place_ids else '') +
                ','.join([str(x.place_id.latitude) + ',' +
                         str(x.place_id.longitude)
                         for x in route.route_place_ids
                         if x.place_id.latitude and x.place_id.longitude]) +
                ',' + str(route.arrival_id.latitude) + ',' +
                str(route.arrival_id.longitude))
            url = "/tms/static/src/googlemaps/get_route.html?" + points
        return {'type': 'ir.actions.act_url',
                'url': url,
                'nodestroy': True,
                'target': 'new'}

    @api.multi
    def get_fuel_efficiency(self, vehicle_id, framework):
        for rec in self:
            fuel = self.env['tms.route.fuelefficiency']
            fuel_id = fuel.search([
                ('route_id', '=', rec.id),
                ('engine_id', '=', vehicle_id.engine_id.id),
                ('type', '=', framework)
            ])
        return fuel_id.performance
