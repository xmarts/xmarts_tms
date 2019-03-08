# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class TmsRouteTollstationCostperaxis(models.Model):
    _name = 'tms.route.tollstation.costperaxis'
    name = fields.Char(string="Ejes", compute="get_name")
    axis = fields.Integer(required=True)
    cost_credit = fields.Float(required=True)
    cost_cash = fields.Float(required=True)
    tollstation_id = fields.Many2one(
        'tms.route.tollstation',
        string='Toll Station')

    @api.multi
    @api.depends('name','axis')
    def get_name(self):

        res = []
        for record in self:
            name = ''
            if record.axis == 1:
                name = 'eje'
            else:
                name = 'ejes'
            record.name = str(record.axis) + ' ' + name