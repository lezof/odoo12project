# -*- coding: utf-8 -*-
from odoo import fields, models,api, _
from datetime import date, timedelta
import logging


class InvoiceCosting(models.Model):
      _name = 'invoice.costing'
      _rec_name = 'name'

      name = fields.Char('Name')
      active = fields.Boolean('Active',default=True)
      shipping_amount =fields.Float('Shipping Cost')
      
      #~ @api.multi
      #~ def invoice_costing(self,vals):
          #~ self.ensure_one()
          #~ vals = {'shipping_amount': shipping_amount}
          #~ account_invoice = self.env['account.invoice']
          #~ print('$$$$$$$$$$$$$$$$$$$',account_invoice)
          #~ return account_invoice.create(vals)

      #~ @api.model
      #~ def create(self, vals):
         #~ res = super(InvoiceCosting, self).create(vals)
         #~ res.invoice_costing()
         #~ return res
    
#~ class City(models.Model):
    #~ _inherit = 'res.city'

    #~ payment_cod   = fields.Float('Payament on Delivery COD')


