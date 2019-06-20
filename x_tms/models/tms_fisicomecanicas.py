# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

class FisicomecanicaVehicle(models.Model):
    _name = 'tms.fisicomecanica.vehicle'

    fisicomecanica_id=fields.Many2one('tms.fisicomecanica')
    
   
    date_vig = fields.Date(string='Fecha de Vigencia')
    folio_verificacion= fields.Char(string="Folio de Verificacion")
    date_veri= fields.Date(string='Fecha Verificacion')
    adjunto = fields.Binary(string="Adjunto")

class TmsFisicomecanicas(models.Model):

    _name = 'tms.fisicomecanica'
    

    name= fields.Char(string="Nombre")
    folio= fields.Char(string="Folio")
    date_fisi = fields.Date(string='Fecha de Fisicomecanicas')
    vehicle_id = fields.Many2one('fleet.vehicle',string='Vehículo', required=True)
    fisicomecanica_ids = fields.One2many(
        'tms.fisicomecanica.vehicle', 'fisicomecanica_id', string='Fisicomecanica')
    notes = fields.Text()
    


