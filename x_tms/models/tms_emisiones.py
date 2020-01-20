# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

class EmisionesVehicle(models.Model):
    _name = 'tms.emisiones.vehicle'

    emisiones_id=fields.Many2one('tms.emisiones')
    date_vig = fields.Date(string='Fecha de Vigencia')
  
    folio_verificacion= fields.Char(string="Folio de Verificacion")
    date_veri= fields.Date(string='Fecha Verificacion')
    
    adjunto = fields.Binary(string="Adjunto")

class TmsFisicomecanicas(models.Model):

    _name = 'tms.emisiones'
    

    name= fields.Char(string="Nombre")
    vehicle_id = fields.Many2one('fleet.vehicle',string='Vehículo', required=True)
    folio= fields.Char(string="Folio")
    emisiones_ids = fields.One2many(
        'tms.emisiones.vehicle', 'emisiones_id', string='Emisiones')
    date_emi = fields.Date(string='Fecha de Emisiones')
    notes = fields.Text()