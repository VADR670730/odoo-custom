# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from datetime import datetime, date
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

class CustomerProductPrice(models.Model):
    _name = 'customer.product.price'
    _description = 'Customer Pricelist Product Price'

    pricelist_id = fields.Many2one('product.pricelist', string='Price List')
    product_id = fields.Many2one('product.product', string='Product')
    price = fields.Float(string='Price')
    partner_id = fields.Many2one('res.partner' , string='Customer')
    sale_uoms = fields.Many2many(related='product_id.sale_uoms', string='Sale UOMS')
    product_uom = fields.Many2one('uom.uom', string='Unit Of Measure', domain="[('id', 'in', sale_uoms)]")
    price_last_updated = fields.Date(string='Price last updated', default=date.today(), readonly=True)
    price_lock = fields.Boolean(string='Price Change Lock', default=False)
    lock_expiry_date = fields.Date(string='Lock Expiry date')


    @api.multi
    def write(self, vals):
        """
        overriden to update price_last_updated
        """
        result = super(CustomerProductPrice, self).write(vals)
        if vals.get('price'):
            self.price_last_updated = date.today()
        return result

    @api.constrains('partner_id')
    def check_partner(self):
        if self.pricelist_id.type == 'customer' and self.pricelist_id.partner_id:
            if self.partner_id.parent_id and self.pricelist_id.partner_id.id == self.partner_id.parent_id.id:
                pass
            elif self.pricelist_id.partner_id.id == self.partner_id.id:
                pass
            else:
                raise ValidationError(_('Partner should be same as pricelist mentioned partner in customer pricelists.'))



    @api.multi
    @api.depends('pricelist_id', 'product_id', 'partner_id')
    def name_get(self):
        result = []
        for record in self:
            name = "%s_%s_%s_%s" % (record.pricelist_id and record.pricelist_id.name or '', record.product_id and record.product_id.name or '', record.product_uom and record.product_uom.name or '', record.partner_id and record.partner_id.name or '')
            result.append((record.id,name))
        return result

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id and self.product_id.uom_id
            self.price = self.product_id.lst_price
        else:
            self.product_uom = False
            self.price = 0.0

    # @api.onchange('price_lock')
    # def onchange_price_lock(self):
    #     if self.price_lock:
    #         if self.env.user.company_id and self.env.user.company_id.price_lock_days:
    #             days = self.env.user.company_id.price_lock_days
    #             self.lock_expiry_date =  date.today()+relativedelta(days=days)
    #     else:
    #         self.lock_expiry_date = False



CustomerProductPrice()
