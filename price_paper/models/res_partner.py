# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'


    destination_code = fields.Char(string='Destination Code')
    corp_name = fields.Char(string='Corporate name ')
    fax_number = fields.Char(string='Fax')
    customer_pricelist_ids = fields.One2many('customer.pricelist', 'partner_id', string="Customer Pricelists")
    customer_code = fields.Char(string='Partner Code', copy=False)
    delivery_day_mon = fields.Boolean(string='Monday')
    delivery_day_tue = fields.Boolean(string='Tuesday')
    delivery_day_wed = fields.Boolean(string='Wednesday')
    delivery_day_thu = fields.Boolean(string='Thursday')
    delivery_day_fri = fields.Boolean(string='Friday')
    delivery_day_sat = fields.Boolean(string='Saturday')
    delivery_day_sun = fields.Boolean(string='Sunday')
    shipping_easiness = fields.Selection([('easy', 'Easy'), ('neutral', 'Neutral'), ('hard', 'Hard')], string='Easiness of shipping')
    change_delivery_days = fields.Boolean(string='Change Zip delivery days')
    zip_delivery_id = fields.Many2one('zip.delivery.day', string='Zip Delivery Days', compute='compute_delivery_day_id')
    zip_delivery_day_mon = fields.Boolean(string='Monday.', related='zip_delivery_id.delivery_day_mon')
    zip_delivery_day_tue = fields.Boolean(string='Tuesday.', related='zip_delivery_id.delivery_day_tue')
    zip_delivery_day_wed = fields.Boolean(string='Wednesday.', related='zip_delivery_id.delivery_day_wed')
    zip_delivery_day_thu = fields.Boolean(string='Thursday.', related='zip_delivery_id.delivery_day_thu')
    zip_delivery_day_fri = fields.Boolean(string='Friday.', related='zip_delivery_id.delivery_day_fri')
    zip_delivery_day_sat = fields.Boolean(string='Saturday.', related='zip_delivery_id.delivery_day_sat')
    zip_delivery_day_sun = fields.Boolean(string='Sunday.', related='zip_delivery_id.delivery_day_sun')
    zip_shipping_easiness = fields.Selection([('easy', 'Easy'), ('neutral', 'Neutral'), ('hard', 'Hard')], string='Easiness of shipping.')


    @api.depends('zip')
    def compute_delivery_day_id(self):
        for rec in self:
            if rec.zip:
                zip_delivery_id = self.env['zip.delivery.day'].search([('zip', '=', rec.zip)])
                rec.zip_delivery_id = zip_delivery_id and zip_delivery_id.id or False
            else:
                rec.zip_delivery_id = False

    @api.model
    def default_get(self, fields_list):
        res = super(ResPartner, self).default_get(fields_list)
        if self.env.user.company_id:
            company = self.env.user.company_id
            res.update({'property_delivery_carrier_id':company.partner_delivery_method_id and company.partner_delivery_method_id.id or False,
            'country_id':company.partner_country_id and company.partner_country_id.id or False,
            'state_id':company.partner_state_id and company.partner_state_id.id or False})
        return res


    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        overriden to display the search result
        based on customer code as well
        """
        res = super(ResPartner, self).name_search(name=name, args=args, operator=operator, limit=limit)
        if name:
            domain = [('customer_code', 'ilike', name)]
            if self._context.get('search_default_supplier', False):
                domain.append(('supplier', '=', True))
            elif self._context.get('search_default_customer', False):
                domain.append(('customer', '=', True))
            customer_code_results = self.search(domain)
            customer_code_results = customer_code_results.name_get()
            res = res + customer_code_results
        return res

    @api.multi
    def name_get(self):
        result = []
        for customer in self:
            name = ''
            if customer.street:
                name += customer.street + ' '
            if customer.city:
                name += customer.city + ' '
            if customer.state_id:
                name += customer.state_id.name
            result.append((customer.id, _('%s (%s)') % (customer.name, name)))
        return result



    @api.constrains('customer_code')
    def check_partner_code(self):
        if self.search([('customer_code', '=ilike', self.customer_code), ('id', '!=', self.id)]):
            raise ValidationError(_('Partner with same Partner code already exists.'))

    @api.model
    def create(self, vals):

        if vals.get('is_company', False):
            if not vals.get('customer_code', False):
                if 'company_id' in vals:
                    while True:
                        customer_code = vals.get('name')[0:3].upper() +  self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('res.partner')
                        if not self.search([('customer_code', '=ilike', customer_code)]):
                            vals['customer_code'] = customer_code
                            break

                else:
                    while True:
                        customer_code = vals.get('name')[0:3].upper() +  self.env['ir.sequence'].next_by_code('res.partner')
                        if not self.search([('customer_code', '=ilike', customer_code)]):
                            vals['customer_code'] = customer_code
                            break

        result = super(ResPartner, self).create(vals)
        if result.customer and result.is_company:
            result.setup_pricelist_for_new_customer()
        return result


    @api.model
    def setup_pricelist_for_new_customer(self):
        pricelist = self.env['product.pricelist'].create({'partner_id': self.id,
                                                          'name': self.customer_code,
                                                          'type': 'customer'})
        self.env['customer.pricelist'].create({'pricelist_id':pricelist.id,
                                               'sequence':1,
                                               'partner_id': self.id})
        return True


ResPartner()

class ResPartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    code = fields.Char(string='Code')


ResPartnerCategory()
