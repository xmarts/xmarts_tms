# -*- coding: utf-8 -*-
# Copyright 2012, Israel Cruz Argil, Argil Consulting
# Copyright 2016, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import logging
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
try:
    from sodapy import Socrata
except ImportError:
    _logger.debug('Cannot `import sodapy`.')


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    driver = fields.Boolean(
        help='Used to define if this person will be used as a Driver')
    tms_advance_account_id = fields.Many2one(
        'account.account', 'Advance Account')
    tms_loan_account_id = fields.Many2one(
        'account.account', 'Loan Account')
    tms_expense_negative_account_id = fields.Many2one(
        'account.account', 'Negative Balance Account')
    operating_unit_id = fields.Many2one(
        'operating.unit', 'Operating Unit',default=lambda self: self.env['operating.unit'].search([('name','=','Mexico')], limit=1).id or self.env['operating.unit'].search([('name','=','México')], limit=1).id or '')
    driver_license = fields.Char(string="License ID")
    license_type = fields.Char()
    days_to_expire = fields.Integer(compute='_compute_days_to_expire')
    income_percentage = fields.Float()
    license_valid_from = fields.Date()
    license_expiration = fields.Date()
    outsourcing = fields.Boolean(string='Outsourcing?')
    employee_category_id = fields.Many2one("hr.employee.category", string="Categoria de empleado")
    num_med_prev = fields.Char(string="Número de medicina preventiva")

    @api.depends('license_expiration')
    def _compute_days_to_expire(self):
        for rec in self:
            date = datetime.now()
            if rec.license_expiration:
                date = datetime.strptime(rec.license_expiration, '%Y-%m-%d')
            now = datetime.now()
            delta = date - now
            rec.days_to_expire = delta.days if delta.days > 0 else 0

    @api.multi
    def get_driver_license_info(self):
        client = Socrata("www.datossct.gob.mx", None)
        for rec in self:
            try:
                driver_license = client.get(
                    '3qhi-59v6', licencia=rec.driver_license)
                license_valid_from = datetime.strptime(
                    driver_license[0]['fecha_inicio_vigencia'],
                    '%Y-%m-%dT%H:%M:%S.%f')
                license_expiration = datetime.strptime(
                    driver_license[0]['fecha_fin_vigencia'],
                    '%Y-%m-%dT%H:%M:%S.%f')
                rec.write({
                    'license_type': driver_license[0][
                        'categoria_de_la_licencia'],
                    'license_valid_from': license_valid_from,
                    'license_expiration': license_expiration,
                })
                client.close()
            except Exception:
                client.close()
                raise ValidationError(_(
                    'The driver license is not in SCT database'))


    monto_info = fields.Float(string="Monto Infonavit", default=0.0)
    periodo_info = fields.Selection([('sem','Semanal'),('quin','Quincenal'),('men','Mensual')], string="Periodo infonavit")
    infonavit_account_id = fields.Many2one('account.account', string='Cuenta infonavit')