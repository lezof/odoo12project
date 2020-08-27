# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api,_

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_shipping = fields.Float('Shipping Cost' ,config_parameter='invoice_costing.invoice_shipping')
    shipping_cost_outside_ksa = fields.Float('Shipping Cost inside KSA' ,config_parameter='invoice_costing.shipping_cost_outside_ksa')
    shipping_packaging = fields.Float('Shipping Packaging',config_parameter='invoice_costing.shipping_packaging')
    shipping_packaging_more_four = fields.Float('Shipping Packaging',config_parameter='invoice_costing.shipping_packaging_more_four')
    payment_cod_inside = fields.Float('Shipping Packaging',config_parameter='invoice_costing.payment_cod_inside')
    payment_cod_outside = fields.Float('Shipping Packaging',config_parameter='invoice_costing.payment_cod_outside')
    product_cost_fife_less = fields.Float('Shipping Packaging',config_parameter='invoice_costing.product_cost_fife_less')
    product_cost_more_fife = fields.Float('Shipping Packaging',config_parameter='invoice_costing.product_cost_more_fife')
    processing_abyas = fields.Float('Shipping Packaging',config_parameter='invoice_costing.processing_abyas')
    bill_shipping_cost = fields.Float(config_parameter='invoice_costing.bill_shipping_cost')
    bill_receiving_product = fields.Float(config_parameter='invoice_costing.bill_receiving_product')
    gift_packaging_cost = fields.Float(config_parameter='invoice_costing.gift_packaging_cost')


    # Relational fields
    invoice_shipping_credit_account_id = fields.Many2one('account.account','Invoice shipping credit account', config_parameter='invoice_costing.invoice_shipping_credit_account_id')
    invoice_shipping_debit_account_id = fields.Many2one('account.account','Invoice shipping debit account', config_parameter='invoice_costing.invoice_shipping_debit_account_id')
    payment_cod_credit_account_id = fields.Many2one('account.account','Payment cod credit account', config_parameter='invoice_costing.payment_cod_credit_account_id')
    payment_cod_debit_account_id = fields.Many2one('account.account','Payment cod debit account', config_parameter='invoice_costing.payment_cod_debit_account_id')
    product_cost_credit_account_id = fields.Many2one('account.account', 'Product Cost Credit Account',
                                                    config_parameter='invoice_costing.product_cost_credit_account_id')
    product_cost_debit_account_id = fields.Many2one('account.account', 'Product Cost Debit Account',
                                                   config_parameter='invoice_costing.product_cost_debit_account_id')
    processing_abyas_credit_account_id = fields.Many2one('account.account','Processing abyas credit account', config_parameter='invoice_costing.processing_abyas_credit_account_id')
    processing_abyas_debit_account_id = fields.Many2one('account.account','Processing abyas debit account', config_parameter='invoice_costing.processing_abyas_debit_account_id')
    shipping_packaging_credit_account_id = fields.Many2one('account.account','Shipping packaging credit account', config_parameter='invoice_costing.shipping_packaging_credit_account_id')
    shipping_packaging_debit_account_id = fields.Many2one('account.account','Shipping packaging debit account', config_parameter='invoice_costing.shipping_packaging_debit_account_id')
    bill_shipping_cost_debit_account_id = fields.Many2one('account.account', config_parameter='invoice_costing.bill_shipping_cost_debit_account_id')
    bill_shipping_cost_credit_account_id = fields.Many2one('account.account', config_parameter='invoice_costing.bill_shipping_cost_credit_account_id')
    bill_receiving_product_debit_account_id = fields.Many2one('account.account', config_parameter='invoice_costing.bill_receiving_product_debit_account_id')
    bill_receiving_product_credit_account_id = fields.Many2one('account.account',config_parameter='invoice_costing.bill_receiving_product_credit_account_id')
    gift_packaging_cost_debit_account_id = fields.Many2one('account.account',config_parameter='invoice_costing.gift_packaging_cost_debit_account_id')
    gift_packaging_cost_credit_account_id = fields.Many2one('account.account',config_parameter='invoice_costing.gift_packaging_cost_credit_account_id')

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        res = self.env['ir.config_parameter'].set_param('invoice_costing.invoice_shipping', self.invoice_shipping)
        res_ship = self.env['ir.config_parameter'].set_param('invoice_costing.shipping_packaging',self.shipping_packaging)
        #~ res_account = self.env['ir.config_parameter'].set_param('invoice_costing.salasa_account_id',self.salasa_account_id)
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        costing = ICPSudo.get_param('invoice_costing.invoice_shipping')
        shipping = ICPSudo.get_param('invoice_costing.shipping_packaging')
        shipping_more_four = ICPSudo.get_param('invoice_costing.shipping_packaging_more_four')
        check_inside_ksa = ICPSudo.get_param('invoice_costing.shipping_cost_outside_ksa')
        cod_inside= ICPSudo.get_param('invoice_costing.payment_cod_inside')
        cod_outside = ICPSudo.get_param('invoice_costing.payment_cod_outside')
        product_fife_less = ICPSudo.get_param('invoice_costing.product_cost_fife_less')
        product_more_fife = ICPSudo.get_param('invoice_costing.product_cost_more_fife')
        processing_abyas = ICPSudo.get_param('invoice_costing.processing_abyas')
        # bill_shipping_cost = ICPSudo.get_param('invoice_costing.bill_shipping_cost')
        # bill_receiving_product = ICPSudo.get_param('invoice_costing.bill_receiving_product')
        #~ account  = ICPSudo.get_param('invoice_costing.salasa_account_id')
        res.update(
            invoice_shipping= float(costing),
            shipping_packaging = float(shipping),
            shipping_packaging_more_four = float(shipping_more_four),
            shipping_cost_outside_ksa = float(check_inside_ksa),
            payment_cod_outside = float(cod_outside),
            payment_cod_inside = float(cod_inside),
            product_cost_fife_less = float(product_fife_less),
            product_cost_more_fife = float(product_more_fife),
            processing_abyas = float(processing_abyas),
            # bill_shipping_cost = float(bill_shipping_cost),
            # bill_receiving_product = float(bill_receiving_product),
            #~ salasa_account_id = account
        )
        return res
    
   
