# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
    pycompat, date_utils
from odoo.tools.misc import formatLang

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from odoo.addons import decimal_precision as dp
import logging
from pprint import pprint
import json


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def get_total_sales_with_invoice(self):
        sale_ids = self.env['sale.order'].search([('invoice_ids', '!=', False)])
        total_paid_invoice = 0.0
        total_other_invoice = 0.0
        count_of_none_invoice = 0.0

        if sale_ids:
            for sale in sale_ids:
                if sale.invoice_ids:
                    total_paid_invoice += sale.amount_total
                    # for line in sale.invoice_ids:
                    #     if line.state == 'paid':
                    #         total_paid_invoice += sale.amount_total
                    #     else:
                    #         total_other_invoice += sale.amount_total
                else:
                    count_of_none_invoice += 1

            raise UserError(
                _('Total Paid Invoice %s AND total other invoice %s  AND number of sale without invoice %s ') % (
                total_paid_invoice, total_other_invoice, count_of_none_invoice))

    # @api.multi
    # def reconcile_lines_welcome(self):
    #     open_invoiced_ids = self.env['account.invoice'].search(
    #         [('state', '=', 'open'), ('residual', '>', '0')],
    #         limit=5)
    #     if open_invoiced_ids:
    #         for invoice in open_invoiced_ids:
    #             if invoice.outstanding_credits_debits_widget != 'false':
    #                 text = invoice.outstanding_credits_debits_widget
    #                 pprint(text)
    #                 line_split = text.split("(", 1)
    #                 text = line_split[0]
    #                 pprint(text)
    #
    #                 dictionary_line_split = json.loads(str(text))
    #                 move_line_id = int(dictionary_line_split['content'][0]['id'])
    #                 invoice.assign_outstanding_credit(move_line_id)

    @api.depends('partner_id')
    def _default_invoice_shipping(self):
        if self.partner_id:
            if self.partner_id.country_id:
                if self.partner_id.country_id.code == 'SA':
                    self.invoice_shipping = self.env['ir.config_parameter'].sudo().get_param(
                        'invoice_costing.invoice_shipping')
            else:
                self.invoice_shipping = self.env['ir.config_parameter'].sudo().get_param(
                    'invoice_costing.shipping_cost_outside_ksa')

        else:
            self.invoice_shipping = self.env['ir.config_parameter'].sudo().get_param(
                'invoice_costing.shipping_cost_outside_ksa')

    @api.model
    def _default_credit_shipping_account(self):
        return int(
            self.env['ir.config_parameter'].sudo().get_param('invoice_costing.invoice_shipping_credit_account_id'))

    @api.model
    def _default_debit_shipping_account(self):
        return int(
            self.env['ir.config_parameter'].sudo().get_param('invoice_costing.invoice_shipping_debit_account_id'))

    @api.model
    def _default_credit_payment_cod(self):
        return int(self.env['ir.config_parameter'].sudo().get_param('invoice_costing.payment_cod_credit_account_id'))

    @api.model
    def _default_debit_payment_cod(self):
        return int(self.env['ir.config_parameter'].sudo().get_param('invoice_costing.payment_cod_debit_account_id'))

    @api.model
    def _default_credit_product_cost(self):
        return int(self.env['ir.config_parameter'].sudo().get_param('invoice_costing.product_cost_credit_account_id'))

    @api.model
    def _default_debit_product_cost(self):
        return int(self.env['ir.config_parameter'].sudo().get_param('invoice_costing.product_cost_debit_account_id'))

    @api.model
    def _default_credit_processing_abyas(self):
        return int(
            self.env['ir.config_parameter'].sudo().get_param('invoice_costing.processing_abyas_credit_account_id'))

    @api.model
    def _default_debit_processing_abyas(self):
        return int(
            self.env['ir.config_parameter'].sudo().get_param('invoice_costing.processing_abyas_debit_account_id'))

    @api.model
    def _default_shipping_packaging_credit(self):
        return int(
            self.env['ir.config_parameter'].sudo().get_param('invoice_costing.shipping_packaging_credit_account_id'))

    @api.model
    def _default_shipping_packaging_debit(self):
        return int(
            self.env['ir.config_parameter'].sudo().get_param('invoice_costing.shipping_packaging_debit_account_id'))

    @api.model
    def _default_gift_packaging_cost_credit(self):
        return int(
            self.env['ir.config_parameter'].sudo().get_param('invoice_costing.gift_packaging_cost_credit_account_id'))

    @api.model
    def _default_gift_packaging_cost_debit(self):
        return int(
            self.env['ir.config_parameter'].sudo().get_param('invoice_costing.gift_packaging_cost_debit_account_id'))

    invoice_shipping = fields.Float('Shipping Cost', compute='_default_invoice_shipping')

    vat_invoice_shipping = fields.Float('Vat shipping cost', compute='_compute_vat_shipping')

    payment_cod = fields.Float('Payment on Delivery COD', compute='onchange_city')

    vat_payment_cod = fields.Float('Vat payment cod', compute='_compute_vat_payment_cod')

    invoice_count = fields.Integer('Invoice Count')

    product_cost = fields.Float('Product Cost', compute='_compute_vals')

    vat_product_cost = fields.Float('Vat Product Cost', compute='_compute_vat_product_cost')

    processing_abyas = fields.Float('Processing abayas', compute='_compute_vat_processing_abyas')

    vat_processing_abyas = fields.Float('Vat processing abyas', compute='_compute_vat_processing_abyas')

    shipping_packaging = fields.Float('Shipping Packaging', compute='_compute_vals')

    vat_shipping_packaging = fields.Float('Vat shippng packaging', compute='_compute_vat_shipping_packaging')

    gift_packaging_cost = fields.Float('Gift Packaging cost', compute='_compute_vals')

    vat_git_packaging_cost = fields.Float('Vat Gift packaging cost', compute='_compute_vals')

    total_costing = fields.Float('Total Costing', compute='_compute_total')

    total_vat = fields.Float('Total vat', compute='_compute_total_vat')

    shipping_cost_credit_account_id = fields.Many2one('account.account', string='Shipping cost credit Account',
                                                      default=_default_credit_shipping_account, readonly=True,
                                                      states={'draft': [('readonly', False)]})

    shipping_cost_debit_account_id = fields.Many2one('account.account', string='Shipping cost debit Account',
                                                     default=_default_debit_shipping_account, readonly=True,
                                                     states={'draft': [('readonly', False)]})

    payment_cod_credit_account_id = fields.Many2one('account.account', string='Payment cod credit account',
                                                    default=_default_credit_payment_cod, readonly=True,
                                                    states={'draft': [('readonly', False)]})

    payment_cod_debit_account_id = fields.Many2one('account.account', string='Payment cod debit account',
                                                   default=_default_debit_payment_cod, readonly=True,
                                                   states={'draft': [('readonly', False)]})

    product_cost_credit_account_id = fields.Many2one('account.account', string='Product Cost credit account',
                                                     default=_default_credit_product_cost, readonly=True,
                                                     states={'draft': [('readonly', False)]})

    product_cost_debit_account_id = fields.Many2one('account.account', string='Product Cost debit account',
                                                    default=_default_debit_product_cost, readonly=True,
                                                    states={'draft': [('readonly', False)]})

    processing_abyas_credit_account_id = fields.Many2one('account.account', string='Processing abyas credit account',
                                                         default=_default_credit_processing_abyas, readonly=True,
                                                         states={'draft': [('readonly', False)]})

    processing_abyas_debit_account_id = fields.Many2one('account.account', string='Processing abyas debit account',
                                                        default=_default_debit_processing_abyas, readonly=True,
                                                        states={'draft': [('readonly', False)]})

    shipping_packaging_credit_account_id = fields.Many2one('account.account',
                                                           string='Shipping packaging credit account',
                                                           default=_default_shipping_packaging_credit, readonly=True,
                                                           states={'draft': [('readonly', False)]})

    shipping_packaging_debit_account_id = fields.Many2one('account.account', string='Shipping packaging debit account',
                                                          default=_default_shipping_packaging_debit, readonly=True,
                                                          states={'draft': [('readonly', False)]})
    gift_packaging_cost_credit_account_id = fields.Many2one('account.account',
                                                            default=_default_gift_packaging_cost_credit)
    gift_packaging_cost_debit_account_id = fields.Many2one('account.account',
                                                           default=_default_gift_packaging_cost_debit)

    @api.depends('payment_cod', 'partner_id')
    def onchange_city(self):
        if self.partner_id:
            if self.partner_id.city:
                if self.partner_id.city in ['الرياض', 'جدة', 'الدمام']:
                    self.payment_cod = self.env['ir.config_parameter'].sudo().get_param(
                        'invoice_costing.payment_cod_inside')
            else:
                self.payment_cod = self.env['ir.config_parameter'].sudo().get_param(
                    'invoice_costing.payment_cod_outside')

        else:
            self.payment_cod = self.env['ir.config_parameter'].sudo().get_param('invoice_costing.payment_cod_outside')

    @api.depends('vat_invoice_shipping', 'invoice_shipping')
    def _compute_vat_shipping(self):
        self.vat_invoice_shipping = self.invoice_shipping * 5 / 100

    @api.depends('vat_payment_cod', 'payment_cod')
    def _compute_vat_payment_cod(self):
        self.vat_payment_cod = self.payment_cod * 5 / 100

    @api.depends('product_cost')
    def _compute_vat_product_cost(self):
        self.vat_product_cost = self.product_cost * 5 / 100

    @api.depends('vat_processing_abyas', 'processing_abyas')
    def _compute_vat_processing_abyas(self):
        if self.type == 'out_invoice':
            self.processing_abyas = 0
        else:
            self.processing_abyas = float(
                self.env['ir.config_parameter'].sudo().get_param('invoice_costing.processing_abyas'))

        self.vat_processing_abyas = self.processing_abyas * 5 / 100

    @api.depends('vat_shipping_packaging', 'shipping_packaging')
    def _compute_vat_shipping_packaging(self):
        self.vat_shipping_packaging = self.shipping_packaging * 5 / 100

    @api.depends('invoice_shipping', 'payment_cod', 'product_cost', 'processing_abyas', 'shipping_packaging')
    def _compute_total(self):
        self.total_costing = self.invoice_shipping + self.payment_cod + self.product_cost + self.processing_abyas + self.shipping_packaging + self.gift_packaging_cost

    @api.depends('vat_invoice_shipping', 'vat_payment_cod', 'vat_processing_abyas', 'vat_shipping_packaging')
    def _compute_total_vat(self):
        self.total_vat = self.vat_invoice_shipping + self.vat_payment_cod + self.vat_processing_abyas + self.vat_shipping_packaging + self.vat_product_cost + self.vat_git_packaging_cost

    @api.multi
    @api.depends('invoice_line_ids')
    def _compute_vals(self):

        products_count = 0.0
        product_unit = 0.0
        gift_count = 0.0
        product_cost_less_than_fife = self.env['ir.config_parameter'].sudo().get_param(
            'invoice_costing.product_cost_fife_less')
        shipping_less_four = self.env['ir.config_parameter'].sudo().get_param('invoice_costing.shipping_packaging')
        shipping_more_four = self.env['ir.config_parameter'].sudo().get_param(
            'invoice_costing.shipping_packaging_more_four')
        gift_packaging_cost = self.env['ir.config_parameter'].sudo().get_param('invoice_costing.gift_packaging_cost')

        for record in self:

            for line in record.invoice_line_ids:
                if line.quantity > 0 and line.product_id.type != 'service':
                    if line.product_id.default_code != 'gift':
                        product_unit += line.quantity
                        products_count += 1
                    else:
                        gift_count += line.quantity

            if product_unit <= 4:
                print(shipping_less_four)
                record.shipping_packaging = float(shipping_less_four)
            else:
                total = (product_unit - 4) * float(shipping_more_four)

                record.shipping_packaging = total + float(shipping_less_four)

            if products_count <= 5:
                record.product_cost = float(product_cost_less_than_fife)
            else:
                more_than_fife = self.env['ir.config_parameter'].sudo().get_param(
                    'invoice_costing.product_cost_more_fife')

                total = (products_count - 5) * float(more_than_fife)
                record.product_cost = total + float(product_cost_less_than_fife)

            if gift_count > 0:
                self.gift_packaging_cost = gift_count * float(gift_packaging_cost)
                self.vat_git_packaging_cost = (self.gift_packaging_cost * 5) / 100

    @api.multi
    def action_move_create(self):
        #         New records will created for invoice shipping cost
        tax_id = self.env['account.tax'].search([('id', '=', '1')]).account_id.id

        res = super(AccountInvoice, self).action_move_create()
        if self.shipping_cost_credit_account_id and self.shipping_cost_debit_account_id and self.payment_cod_credit_account_id and self.payment_cod_debit_account_id and self.product_cost_credit_account_id and self.product_cost_debit_account_id and self.processing_abyas_credit_account_id and self.processing_abyas_debit_account_id and self.shipping_packaging_credit_account_id and self.shipping_packaging_debit_account_id and self.gift_packaging_cost_debit_account_id and self.gift_packaging_cost_credit_account_id and self.type == 'out_invoice' and self.state == 'draft' and _(
                'Draft Invoice'):
            debit_move_id = self.move_id
            tax_id = self.env['account.tax'].search([('id', '=', '1')]).account_id.id

            if self.type == 'out_invoice':

                debit_move_id.write({'line_ids': [
                    (0, 0, {'name': 'Shipping Cost',
                            'credit': 0.0,
                            'debit': self.invoice_shipping,
                            'account_id': self.shipping_cost_debit_account_id.id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Shipping Cost',
                            'debit': 0.0,
                            'credit': self.invoice_shipping + self.vat_invoice_shipping,
                            'account_id': self.shipping_cost_credit_account_id.id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Vat Shipping Cost',
                            'credit': 0.0,
                            'debit': self.vat_invoice_shipping,
                            'account_id': tax_id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Payment Cod',
                            'credit': 0.0,
                            'debit': self.payment_cod,
                            'account_id': self.payment_cod_debit_account_id.id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Payment Cod',
                            'debit': 0.0,
                            'credit': self.payment_cod + self.vat_payment_cod,
                            'account_id': self.payment_cod_credit_account_id.id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Vat Payment Cod',
                            'credit': 0.0,
                            'debit': self.vat_payment_cod,
                            'account_id': tax_id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Product Cost',
                            'credit': 0.0,
                            'debit': self.product_cost,
                            'account_id': self.product_cost_debit_account_id.id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Product Cost',
                            'debit': 0.0,
                            'credit': self.product_cost + self.vat_product_cost,
                            'account_id': self.product_cost_credit_account_id.id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Vat Product Cost',
                            'credit': 0.0,
                            'debit': self.vat_product_cost,
                            'account_id': tax_id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Shipping Packaging',
                            'credit': 0.0,
                            'debit': self.shipping_packaging,
                            'account_id': self.shipping_packaging_debit_account_id.id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Shipping Packaging',
                            'debit': 0.0,
                            'credit': self.shipping_packaging + self.vat_shipping_packaging,
                            'account_id': self.shipping_packaging_credit_account_id.id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Vat Shipping Packaging',
                            'credit': 0.0,
                            'debit': self.vat_shipping_packaging,
                            'account_id': tax_id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Gift Packaging Cost',
                            'credit': 0.0,
                            'debit': self.gift_packaging_cost,
                            'account_id': self.gift_packaging_cost_debit_account_id.id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Gift Packaging Cost',
                            'debit': 0.0,
                            'credit': self.gift_packaging_cost + self.vat_git_packaging_cost,
                            'account_id': self.gift_packaging_cost_credit_account_id.id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Vat Gift Packaging',
                            'credit': 0.0,
                            'debit': self.vat_git_packaging_cost,
                            'account_id': tax_id,
                            'partner_id': self.partner_id.id}),
                ]})
            else:
                debit_move_id.write({'line_ids': [
                    (0, 0, {'name': 'Shipping Cost',
                            'credit': 0.0,
                            'debit': self.invoice_shipping + self.vat_invoice_shipping,
                            'account_id': self.shipping_cost_debit_account_id.id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Shipping Cost',
                            'debit': 0.0,
                            'credit': self.invoice_shipping,
                            'account_id': self.shipping_cost_credit_account_id.id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Vat Shipping Cost',
                            'debit': 0.0,
                            'credit': self.vat_invoice_shipping,
                            'account_id': tax_id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Payment Cod',
                            'credit': 0.0,
                            'debit': self.payment_cod + self.vat_payment_cod,
                            'account_id': self.payment_cod_debit_account_id.id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Payment Cod',
                            'debit': 0.0,
                            'credit': self.payment_cod,
                            'account_id': self.payment_cod_credit_account_id.id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Vat Payment Cod',
                            'debit': 0.0,
                            'credit': self.vat_payment_cod,
                            'account_id': tax_id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Product Cost',
                            'credit': 0.0,
                            'debit': self.product_cost + self.vat_product_cost,
                            'account_id': self.product_cost_debit_account_id.id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Product Cost',
                            'debit': 0.0,
                            'credit': self.product_cost,
                            'account_id': self.product_cost_credit_account_id.id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Vat Product Cost',
                            'debit': 0.0,
                            'credit': self.vat_product_cost,
                            'account_id': tax_id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Processing abayas',
                            'credit': 0.0,
                            'debit': self.processing_abyas + self.vat_processing_abyas,
                            'account_id': self.processing_abyas_debit_account_id.id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Processing abayas',
                            'debit': 0.0,
                            'credit': self.processing_abyas,
                            'account_id': self.processing_abyas_credit_account_id.id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Vat Processing abayas',
                            'debit': 0.0,
                            'credit': self.vat_processing_abyas,
                            'account_id': tax_id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Shipping Packaging',
                            'credit': 0.0,
                            'debit': self.shipping_packaging + self.vat_shipping_packaging,
                            'account_id': self.shipping_packaging_debit_account_id.id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Shipping Packaging',
                            'debit': 0.0,
                            'credit': self.shipping_packaging,
                            'account_id': self.shipping_packaging_credit_account_id.id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Vat Shipping Packaging',
                            'debit': 0.0,
                            'credit': self.vat_shipping_packaging,
                            'account_id': tax_id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Gift Packaging Cost',
                            'credit': 0.0,
                            'debit': self.gift_packaging_cost + self.vat_git_packaging_cost,
                            'account_id': self.gift_packaging_cost_debit_account_id.id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Gift Packaging Cost',
                            'debit': 0.0,
                            'credit': self.gift_packaging_cost,
                            'account_id': self.gift_packaging_cost_credit_account_id.id,
                            'partner_id': self.partner_id.id}),

                    (0, 0, {'name': 'Vat Gift Packaging',
                            'debit': 0.0,
                            'credit': self.vat_git_packaging_cost,
                            'account_id': tax_id,
                            'partner_id': self.partner_id.id}),
                ]})


        elif not self.shipping_cost_credit_account_id and self.shipping_cost_debit_account_id and self.payment_cod_credit_account_id and self.payment_cod_debit_account_id and self.processing_abyas_credit_account_id and self.processing_abyas_debit_account_id and self.shipping_packaging_credit_account_id and self.shipping_packaging_debit_account_id:
            raise ValidationError(_('Please Check payment accounts .'))
        return res
