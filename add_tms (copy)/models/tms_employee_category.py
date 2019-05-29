# -*- coding: utf-8 -*-

from odoo import models, fields, api

class tms_employee_salary(models.Model):
    _name = 'hr.employee.salary'
    name = fields.Char(string="Concepto")
    tipo = fields.Selection([('percepcion','Percepción'),('deduccion','Deducción')], string="Tipo")
    monto = fields.Float(string="Monto")
    hr_emp_cat_id = fields.Many2one("hr.employee.category")

class tms_categories_events(models.Model):


	_name = 'hr.employee.category'
	name = fields.Char('Etiqueta del empleado')
	periodo = fields.Selection([('sem','Semanal'),('quin','Quincenal'),('men','Mensual')], string="Periodo de nomina")
	employee_salary_ids = fields.One2many("hr.employee.salary", "hr_emp_cat_id", string="Detalles de salario")
