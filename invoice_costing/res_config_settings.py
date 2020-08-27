# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api,_

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_shipping = fields.Float('Shipping Cost' ,config_parameter='invoice_costing.invoice_shipping')
    shipping_packaging = fields.Float('Shipping Packaging',config_parameter='invoice_costing.shipping_packaging')
    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        res = self.env['ir.config_parameter'].set_param('invoice_costing.invoice_shipping', self.invoice_shipping)
        res_ship = self.env['ir.config_parameter'].set_param('invoice_costing.shipping_packaging',self.shipping_packaging)
        
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        costing = ICPSudo.get_param('invoice_costing.invoice_shipping')
        shipping = ICPSudo.get_param('invoice_costing.shipping_packaging')
        res.update(
            invoice_shipping= float(costing),
            shipping_packaging = float(shipping)
        )
        return res
    
   
