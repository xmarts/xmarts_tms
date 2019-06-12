# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class TmsFisicomecanicas(models.Model):

    _name = 'tms.fisicomecanica'
    

    name= fields.Char(string="Nombre")
    folio= fields.Char(string="Folio")
    date_fisi = fields.Date(string='Fecha de Fisicomecanicas')
    date_vig = fields.Date(string='Fecha de Vigencia')
    folio_verificacion= fields.Char(string="Folio de Verificacion")
    date_veri= fields.Date(string='Fecha Verificacion')
    notes = fields.Text()