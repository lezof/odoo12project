from odoo import api, fields, models , _
from odoo.exceptions import ValidationError


class BillAccountInvoice(models.Model):
    _inherit = 'account.invoice'


    @api.model
    def _default_debit_bill_shipping_cost(self):
        return int(
            self.env['ir.config_parameter'].sudo().get_param('invoice_costing.bill_shipping_cost_debit_account_id'))

    @api.model
    def _default_credit_bill_shipping_cost(self):
        return int(
            self.env['ir.config_parameter'].sudo().get_param('invoice_costing.bill_shipping_cost_credit_account_id'))

    @api.model
    def _default_debit_bill_receiving_product(self):
        return int(
            self.env['ir.config_parameter'].sudo().get_param('invoice_costing.bill_receiving_product_debit_account_id'))

    @api.model
    def _default_credit_bill_receiving_product(self):
        return int(self.env['ir.config_parameter'].sudo().get_param(
            'invoice_costing.bill_receiving_product_credit_account_id'))

    bill_shipping_cost = fields.Float(compute='_compute_shipping_receiving_value')
    bill_receiving_product = fields.Float(compute='_compute_shipping_receiving_value')
    vat_bill_shipping_cost = fields.Float(compute='_compute_shipping_receiving_value')
    vat_bill_receiving_product = fields.Float(compute='_compute_shipping_receiving_value')

    # Relational fields
    bill_shipping_cost_debit_account_id = fields.Many2one('account.account', default=_default_debit_bill_shipping_cost)
    bill_shipping_cost_credit_account_id = fields.Many2one('account.account',
                                                           default=_default_credit_bill_shipping_cost)
    bill_receiving_product_debit_account_id = fields.Many2one('account.account',
                                                              default=_default_debit_bill_receiving_product)
    bill_receiving_product_credit_account_id = fields.Many2one('account.account',
                                                               default=_default_credit_bill_receiving_product)

    @api.multi
    @api.depends('invoice_line_ids')
    def _compute_shipping_receiving_value(self):



        for record in self:

            product_unit = 0.0
            bill_shipping_cost = float(
                self.env['ir.config_parameter'].sudo().get_param('invoice_costing.bill_shipping_cost'))
            bill_receiving_product = float(
                self.env['ir.config_parameter'].sudo().get_param('invoice_costing.bill_receiving_product'))

            for line in record.invoice_line_ids:
                if line.quantity > 0 and line.product_id.type != 'service' and line.product_id.default_code != 'gift':
                    product_unit += line.quantity

            record.bill_shipping_cost = bill_shipping_cost * product_unit
            record.bill_receiving_product = bill_receiving_product * product_unit
            record.vat_bill_shipping_cost = (record.bill_shipping_cost * 5) / 100
            record.vat_bill_receiving_product = (record.bill_receiving_product * 5) / 100

    @api.multi
    def action_move_create(self):
        res = super(BillAccountInvoice, self).action_move_create()
        if self.bill_shipping_cost_debit_account_id and self.bill_shipping_cost_credit_account_id and self.bill_receiving_product_debit_account_id and self.bill_receiving_product_credit_account_id and self.type == 'in_invoice' and self.state == 'draft' and _(
                'Draft Invoice'):
            debit_move_id = self.move_id

            debit_move_id.write({'line_ids': [(0, 0, {'name': 'Shipping Cost',
                                                      'credit': 0.0,
                                                      'debit': self.bill_shipping_cost + self.vat_bill_shipping_cost,
                                                      'account_id': self.bill_shipping_cost_credit_account_id.id,
                                                      'partner_id': self.partner_id.id}),

                                              (0, 0, {'name': 'Shipping Cost',
                                                      'debit': 0.0,
                                                      'credit': self.bill_shipping_cost,
                                                      'account_id': self.bill_shipping_cost_debit_account_id.id,
                                                      'partner_id': self.partner_id.id}),

                                              (0, 0, {'name': 'Vat Shipping Cost',
                                                      'debit': 0.0,
                                                      'credit': self.vat_bill_shipping_cost,
                                                      'account_id': 1 , # 1 is id of tax
                                                      'partner_id': self.partner_id.id}),

                                              (0, 0, {'name': 'Receive Product',
                                                      'credit': 0.0,
                                                      'debit': self.bill_receiving_product + self.vat_bill_receiving_product,
                                                      'account_id': self.bill_receiving_product_debit_account_id.id,
                                                      'partner_id': self.partner_id.id}),

                                              (0, 0, {'name': 'Receive Product',
                                                      'debit': 0.0,
                                                      'credit': self.bill_receiving_product,
                                                      'account_id': self.bill_receiving_product_credit_account_id.id,
                                                      'partner_id': self.partner_id.id}),
                                              (0, 0, {'name': 'Vat Receive Product',
                                                      'debit': 0.0,
                                                      'credit': self.vat_bill_receiving_product,
                                                      'account_id': 1 , # 1 is id of tax
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
                                                      'account_id': 1 , # 1 is id of tax
                                                      'partner_id': self.partner_id.id}),

                                              ]})
        elif not self.bill_shipping_cost_debit_account_id and self.bill_shipping_cost_credit_account_id and self.bill_receiving_product_debit_account_id and self.bill_receiving_product_credit_account_id :
            raise ValidationError(_('Please choose the salasa account for shipping cost.'))
        return res
