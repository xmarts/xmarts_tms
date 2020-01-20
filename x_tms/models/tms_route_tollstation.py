# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class TmsRouteTollstation(models.Model):
    _name = 'tms.route.tollstation'

    name = fields.Char(required=True)
    subname = fields.Char(compute="compute_subname")
    place_id = fields.Many2one('tms.place', string="Place", required=True)
    partner_id = fields.Many2one('res.partner', string="Partner")
    route_ids = fields.Many2many('tms.route', string="Routes")
    credit = fields.Boolean()
    cost_per_axis_ids = fields.One2many(
        'tms.route.tollstation.costperaxis',
        'tollstation_id',
        string='Cost per Axis')
    active = fields.Boolean(default=True)

    @api.one
    def compute_subname(self):
        self.subname = str(self.name).upper()


    # @api.model
    # def _get_field_axis(self):
    #     related_model_id = self.env['tms.route.tollstation.costperaxis'].search([('tollstation_id','=',self.id)], limit=1).id
    #     return related_model_id

    # ejes = fields.Many2one("tms.route.tollstation.costperaxis",string="# Ejes",default=_get_field_axis)
    # costo_caseta = fields.Float(string="Costo caseta", compute="get_costo")



    # @api.multi
    # @api.depends('credit','costo_caseta','ejes')
    # def get_costo(self):
    #     for record in self:
    #         costo = 0.0
    #         if record.credit == True:
    #             costo = record.ejes.cost_credit
    #         else:
    #             costo = record.ejes.cost_cash
    #         record.costo_caseta = costo
