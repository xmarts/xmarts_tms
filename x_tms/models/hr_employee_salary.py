# -*- coding: utf-8 -*-

from __future__ import division

from datetime import datetime, date, time, timedelta
import tempfile
import base64
import os

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class tms_employee_salary(models.Model):
    _name = 'hr.employee.salary'
    
    name = fields.Char(string="Concepto")
    tipo = fields.Selection([('percepcion','Percepción'),('deduccion','Deducción')], string="Tipo")
    monto = fields.Float(string="Monto por periodo")
    periodo = fields.Selection([('sem','Semanal'),('quin','Quincenal'),('men','Mensual')], string="Periodo de nomina")
    hr_emp_cat_id = fields.Many2one("hr.employee.category")
    expense_id = fields.Many2one("tms.expense")


