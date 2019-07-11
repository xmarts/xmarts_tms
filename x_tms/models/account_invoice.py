# -*- coding: utf-8 -*-
# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError



class AccountInvoice_travel(models.Model):
    _name = 'account.invoice.travel'
    travel_id = fields.Many2one('tms.travel',string="Viaje")
    
  
  
    cliente_id = fields.Many2one(related='travel_id.cliente_id',readonly=True)
    flete_cliente = fields.Float(string='Flete cliente', related='travel_id.flete_cliente',readonly=True)
   
    date = fields.Datetime(
        'Date  registered', related='travel_id.date',readonly=True)
    odometer = fields.Float(
        'Unit Odometer (mi./km)',related='travel_id.odometer',readonly=True)
    state = fields.Selection([
        ('draft', 'Pendiente'), ('progress', 'En progreso'), ('done', 'Hecho'),
        ('cancel', 'Cancelado'), ('closed', 'Cerrado')],
        related='travel_id.state',readonly=True)
    line = fields.Boolean(default=False)
    account=fields.Many2one('account.invoice', string='Factura')

    # @api.multi
    # def create(self, vals):
    #     for rec in self:
    #         res = super(AccountInvoice_travel, self).create(vals)
    #         product_felte_obj = self.env['product.product'].search([('es_flete','=',True)], limit=1)
    #         account_analytic = self.env['account.analytic.account'].search([('name','=',rec.travel_id.unit_id.name)], limit=1)
    #         if not account_analytic:
    #             account_analytic=self.env['account.analytic.account'].create({                      
    #                 'name':rec.travel_id.unit_id.name,                             
    #                 })
    #         taxes = []
    #         for t in product_felte_obj.taxes_id:
    #             taxes.append(t.id)  
    #         self.env['account.invoice.line'].create({           
    #         #'sequence':10,
    #         'product_id':product_felte_obj.id,
    #         'origin':'Cobro por el flete del viaje - ' + rec.travel_id.name,
    #         'name':'Cobro por el flete del viaje - ' + rec.travel_id.name,
    #         'company_id':rec.account.company_id.id,
    #         'invoice_id':rec.account.id,
    #         'travels_ids':rec.id,
    #         'account_id':product_felte_obj.categ_id.property_account_income_categ_id.id,
    #         'account_analytic_id':account_analytic.id,
    #         #'analytic_tag_ids':rec.
    #         'quantity':1.00,
    #         'uom_id':product_felte_obj.uom_id.id,
    #         'price_unit':rec.travel_id.flete_cliente,
    #         #'discount':0.00,
    #         'invoice_line_tax_ids':[(6, 0, taxes)],
    #         #'price_subtotal':100.00,
    #         #'currency_id':34
    #         })

    #         self.write({'line':True})

    #         rec.write({'account_id':rec.account.id})
    #         return res

    @api.multi
    def unlink(self):
        for rec in self:
            travels = self.env['account.invoice.line'].search([('travels_ids', '=', rec.id)]).unlink()

            for acc in rec.travel_id:
                acc.write({'account_id':False})
            #self.account._onchange_invoice_line_ids()     
            return super(AccountInvoice_travel, self).unlink()

class AccountInvoice_line(models.Model):
    _inherit = 'account.invoice.line'

    travels_ids = fields.Many2one('account.invoice.travel', string='Viaje')


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    waybill_ids = fields.One2many(
        'tms.waybill', 'invoice_id', string="Waybills", readonly=True)
    travel_ids = fields.One2many('account.invoice.travel', 'account', string='Travels')

    @api.onchange('travel_ids')
    def _onchange_travel_ids(self):
        taxes_grouped = self.get_taxes_value()
        tax_lines = self.tax_line_ids.filtered('manual')
        for tax in taxes_grouped.values():
            tax_lines += tax_lines.new(tax)
        self.tax_line_ids = tax_lines
        return

    # @api.depends('invoice_line_ids')
    # @api.multi
    # def calcula_inv_lines(self):
    #     for rec in self:
    #         for x in rec.invoice_line_ids:
    #             if x.travels_ids:
    #                 x.quantity = 1

    # @api.onchange('travel_ids')
    # def _onchange_invoice_line_idss(self):
    #     taxes_grouped = {}
    #     round_curr = self.currency_id.round
    #     for line in self.travel_ids:
    #         price_unit = line.travel_id.flete_cliente 
    #         product_felte_obj = self.env['product.product'].search([('es_flete','=',True)], limit=1)
    #         taxes = product_felte_obj.taxes_id.compute_all(price_unit, self.currency_id, 1, product_felte_obj, self.partner_id)['taxes']
    #         for tax in taxes:
    #             val = self._prepare_tax_line_vals(line, tax)
    #             key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)

    #             if key not in tax_grouped:
    #                 tax_grouped[key] = val
    #                 tax_grouped[key]['base'] = round_curr(val['base'])
    #             else:
    #                 tax_grouped[key]['amount'] += val['amount']
    #                 tax_grouped[key]['base'] += round_curr(val['base'])
    #     tax_lines = self.tax_line_ids.filtered('manual')
    #     for tax in taxes_grouped.values():
    #         tax_lines += tax_lines.new(tax)
    #     self.tax_line_ids = tax_lines
    #     return
   
    @api.multi
    def get_taxes_value(self):
        tax_grouped = {}
        round_curr = self.currency_id.round
        for line in self.travel_ids:
            price_unit = line.travel_id.flete_cliente #* (1 - (line.discount or 0.0) / 100.0)
            product_felte_obj = self.env['product.product'].search([('es_flete','=',True)], limit=1)
            product_id=product_felte_obj.id
            taxes = product_felte_obj.taxes_id.compute_all(price_unit, self.currency_id, 1.00, product_id, self.partner_id)['taxes']
            for tax in taxes:
                val = self._prepare_tax_line_val(line, tax)
                key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)

                if key not in tax_grouped:
                    tax_grouped[key] = val
                    tax_grouped[key]['base'] = round_curr(val['base'])
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += round_curr(val['base'])
        return tax_grouped

    @api.multi
    def _prepare_tax_line_val(self, line, tax):
        """ Prepare values to create an account.invoice.tax line

        The line parameter is an account.invoice.line, and the
        tax parameter is the output of account.tax.compute_all().
        """
        product_felte_obj = self.env['product.product'].search([('es_flete','=',True)], limit=1)
        vals = {
            'invoice_id': self.id,
            'name': tax['name'],
            'tax_id': tax['id'],
            'amount': tax['amount'],
            'base': tax['base'],
            'manual': False,
            'sequence': tax['sequence'],
            'account_analytic_id': tax['analytic'] and line.account_analytic_id.id or False,
            'account_id': self.type in ('out_invoice', 'in_invoice') and (tax['account_id'] or product_felte_obj.categ_id.property_account_income_categ_id.id,) or (tax['refund_account_id'] or product_felte_obj.categ_id.property_account_income_categ_id.id,),
        }
        if not vals.get('account_analytic_id')  and vals['account_id'] == product_felte_obj.categ_id.property_account_income_categ_id.id:
            vals['account_analytic_id'] = False

        return vals
    @api.multi
    def write(self, values):
        for rec in self:
            res = super(AccountInvoice, self).write(values)            
            if res:
                product_felte_obj = self.env['product.product'].search([('es_flete','=',True)], limit=1)

                for recs in rec.travel_ids:

                    for acc in recs.travel_id:
                        account_analytic = self.env['account.analytic.account'].search([('name','=',acc.unit_id.name)], limit=1)
                        if account_analytic:
                            taxes = []
                            for t in product_felte_obj.taxes_id:
                                taxes.append(t.id)                        
                            if recs.line == False:
                                do=self.env['account.invoice.line'].create({           
                                #'sequence':10,
                                'product_id':product_felte_obj.id,
                                'origin':'Cobro por el flete del viaje - ' + acc.name,
                                'name':'Cobro por el flete del viaje - ' + acc.name,
                                'company_id':self.company_id.id,
                                'invoice_id':recs.account.id,
                                'travels_ids':recs.id,
                                'account_id':product_felte_obj.categ_id.property_account_income_categ_id.id,
                                'account_analytic_id':account_analytic.id,
                                #'analytic_tag_ids':rec.
                                'quantity':1.00,
                                'uom_id':product_felte_obj.uom_id.id,
                                'price_unit':acc.flete_cliente,
                                #'discount':0.00,
                                'invoice_line_tax_ids':[(6, 0, taxes)],
                                #'price_subtotal':0.00,
                                #'currency_id':34
                                })
                              


                        if not account_analytic:
                            account=self.env['account.analytic.account'].create({                      
                                'name':acc.unit_id.name,                             
                                })
                            if account:
                                taxes = []
                                for t in product_felte_obj.taxes_id:
                                    taxes.append(t.id)                        
                                if recs.line == False:
                                    do=self.env['account.invoice.line'].create({           
                                    #'sequence':10,
                                    'product_id':product_felte_obj.id,
                                    'origin':'Cobro por el flete del viaje - ' + acc.name,
                                    'name':'Cobro por el flete del viaje - ' + acc.name,
                                    'company_id':self.company_id.id,
                                    'invoice_id':recs.account.id,
                                    'travels_ids':recs.id,
                                    'account_id':product_felte_obj.categ_id.property_account_income_categ_id.id,
                                    'account_analytic_id':account.id,
                                    #'analytic_tag_ids':rec.
                                    'quantity':1.00,
                                    'uom_id':product_felte_obj.uom_id.id,
                                    'price_unit':acc.flete_cliente,
                                    #'discount':0.00,
                                    'invoice_line_tax_ids':[(6, 0, taxes)],
                                    #'price_subtotal':0.00,
                                    #'currency_id':34
                                    })


        #       taxes_grouped = self.get_taxes_values()
        # tax_lines = self.tax_line_ids.filtered('manual')
        # for tax in taxes_grouped.values():
        #     tax_lines += tax_lines.new(tax)
        # self.tax_line_ids = tax_lines

            for x in rec.travel_ids:
                x.write({'line':True})
                for acc in x.travel_id:
                    acc.write({'account_id':x.account.id})
            return res

   


 
 
    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if self.waybill_ids:
            self.currency_id = self.waybill_ids[0].currency_id.id
        else:
            return super(AccountInvoice, self)._onchange_journal_id()

    @api.multi
    def action_invoice_automatico(self):
        entrada =self.env['tms.travel']      
        lines = entrada.search([('account_id','=',False),('facturar','=',False), ('state','in', ['done','closed']),('cliente_id','=',self.partner_id.id)])
        if not lines:
            raise UserError(_('No hay mas lineas por Agregar'))
   
        for rec in lines:
            do=self.env['account.invoice.travel'].create({           
            'travel_id':rec.id,
            'state':rec.state,
            'date':rec.date,
            'cliente_id':rec.cliente_id,
            'flete_cliente':rec.flete_cliente,
            'odometer':rec.odometer,
            'account':self.id,
            #'line':True
            })
            if do:
                entradas =self.env['account.invoice.travel']      
                line = entradas.search([('account','=',do.account.id)])
                for rec in line:
                    product_felte_obj = self.env['product.product'].search([('es_flete','=',True)], limit=1)
                    for l in rec.travel_id:
                        l.write({'account_id':do.account.id})
                        account_analytic = self.env['account.analytic.account'].search([('name','=',l.unit_id.name)], limit=1)                                                    
                        if account_analytic:
                            taxes = []
                            for t in product_felte_obj.taxes_id:
                                taxes.append(t.id)            
                            if rec.line == False:
                                dos=self.env['account.invoice.line'].create({           
                                #'sequence':10,
                                'product_id':product_felte_obj.id,
                                'origin':'Cobro por el flete del viaje - ' + l.name,
                                'name':'Cobro por el flete del viaje - ' + l.name,
                                'company_id':self.company_id.id,
                                'invoice_id':rec.account.id,
                                'travels_ids':rec.id,
                                'account_id':product_felte_obj.categ_id.property_account_income_categ_id.id,
                                'account_analytic_id':account_analytic.id,
                                #'analytic_tag_ids':rec.
                                'quantity':1.00,
                                'uom_id':product_felte_obj.uom_id.id,
                                'price_unit':l.flete_cliente,
                                #'discount':0.00,
                                'invoice_line_tax_ids':[(6, 0, taxes)],
                                #'price_subtotal':0.00,
                                #'currency_id':34
                                })
                                if dos:
                                    rec.write({'line':True})

                                    taxes_grouped = self.get_taxes_value()
                                    tax_lines = self.tax_line_ids.filtered('manual')
                                    for tax in taxes_grouped.values():
                                        tax_lines += tax_lines.new(tax)
                                    self.tax_line_ids = tax_lines
                        if not account_analytic:
                            account=self.env['account.analytic.account'].create({                      
                                'name':l.unit_id.name,                             
                                })
                            if account:
                                taxes = []
                                for t in product_felte_obj.taxes_id:
                                    taxes.append(t.id)            
                                if rec.line == False:        
                                    dos=self.env['account.invoice.line'].create({           
                                    #'sequence':10,
                                    'product_id':product_felte_obj.id,
                                    'origin':'Cobro por el flete del viaje - ' + l.name,
                                    'name':'Cobro por el flete del viaje - ' + l.name,
                                    'company_id':self.company_id.id,
                                    'invoice_id':rec.account.id,
                                    'travels_ids':rec.id,
                                    'account_id':t.account_id.id,
                                    'account_analytic_id':account.id,
                                    #'analytic_tag_ids':rec.
                                    'quantity':1.00,
                                    'uom_id':product_felte_obj.uom_id.id,
                                    'price_unit':l.flete_cliente,
                                    #'discount':0.00,
                                    'invoice_line_tax_ids':[(6, 0, taxes)],
                                    #'price_subtotal':0.00,
                                    #'currency_id':34
                                    })
                                    if dos:
                                        rec.write({'line':True})
                                        taxes_grouped = self.get_taxes_value()
                                        tax_lines = self.tax_line_ids.filtered('manual')
                                        for tax in taxes_grouped.values():
                                            tax_lines += tax_lines.new(tax)
                                        self.tax_line_ids = tax_lines
                
         