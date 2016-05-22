 # -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.tools.translate import _
import datetime

class BeesdooProduct(models.Model):
    _inherit = "product.template"

    eco_label = fields.Many2one('beesdoo.product.label', domain = [('type', '=', 'eco')])
    local_label = fields.Many2one('beesdoo.product.label', domain = [('type', '=', 'local')])
    fair_label = fields.Many2one('beesdoo.product.label', domain = [('type', '=', 'fair')])
    origin_label = fields.Many2one('beesdoo.product.label', domain = [('type', '=', 'delivery')])

    main_seller_id = fields.Many2one('res.partner', compute='_compute_main_seller_id', store=True)

    label_to_be_printed = fields.Boolean('Print label?')
    label_last_printed = fields.Datetime('Label last printed on')



    @api.one
    @api.depends('weight', 'display_unit')
    def get_display_weight(self):
        if self.display_unit:
            self.display_weight = self.weight * self.display_unit.factor

    @api.one
    def get_total_with_vat(self):
        tax_amount_sum = 0.0
        if hasattr(self, 'taxes_id'):
            for tax in self.taxes_id:
                tax_amount_sum = tax_amount_sum + tax.amount
        self.total_with_vat = self.list_price * (100.0 + tax_amount_sum) / 100

    @api.one
    def get_total_with_vat_by_unit(self):
        if self.display_weight > 0:
            self.total_with_vat_by_unit = self.total_with_vat / self.weight

    @api.one
    @api.depends('seller_ids', 'seller_ids.date_start')
    def _compute_main_seller_id(self):
        # Calcule le vendeur associé qui a la date de début la plus récente et plus petite qu’aujourd’hui
        sellers_ids = self.seller_ids.sorted(key=lambda seller: seller.date_start, reverse=True)
        self.main_seller_id = sellers_ids and sellers_ids[0].name or False

    @api.one
    def _request_label_printing(self):
        print("request_printing")
        self.label_to_be_printed = True

    @api.one
    def _set_label_as_printed(self):
        self.label_to_be_printed = False
        self.label_last_printed = datetime.datetime.now()



class BeesdooProductLabel(models.Model):
    _name = "beesdoo.product.label"

    name = fields.Char()
    type = fields.Selection([('eco', 'Écologique'), ('local', 'Local'), ('fair', 'Équitable'), ('delivery', 'Distribution')])
    color_code = fields.Char()
