# -*- coding: utf-8 -*-


from odoo import fields, models


class ResCategory(models.Model):

    _inherit = 'res.partner.category'
    name=fields.Char(string='Nombre de etiqueta', requiered=True)
    parent_id=fields.Many2one('res.partner.category', string='Categoría padre')
    active=fields.Boolean(string='Activo')