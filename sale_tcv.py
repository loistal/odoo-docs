# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-Today OpenERP SA (<http://www.openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging
import openerp.addons.decimal_precision as dp

from openerp import models, fields, api

_logger = logging.getLogger(__name__)

# Leads == potential customers
class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    date_arrivee = fields.Date(string="Arrivée")
    date_depart = fields.Date(string='Départ')
    mariage = fields.Boolean(string='Mariage')
    date_mariage = fields.Date(string='Date Mariage')
    

# Defines a single line in a Devis (under the Ligne de la command tab)
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    ########################################
    ##              FUNCTIONS             ##
    ########################################
    # overwrite de la fonction presente dans sale/sale.py ligne 860
    def _calc_line_base_price(self, cr, uid, line, context=None):

        # Get the sale_order id
        sale_order = self.pool.get('sale.order').browse(cr, uid, line.order_id.id, context=context)
        tva_tx = sale_order.com_tva
        
        # Compute totql commission
        total_commission = (line.line_com_HT*(1+tva_tx))

        if line.product_uom_qty==0:
            return 0
        else:
            # base price is a combination of unit price, discount, and commission
            return (line.price_unit * (1 - (line.discount or 0.0) / 100.0) + (total_commission/line.product_uom_qty))
    
    # calcul les com sur une ligne
    # Commission for 1 line
    def _calc_line_com(self, cr, uid, line, context=None):
        return self.line_com_tx * self.product_uom_qty * self.price_unit / 100.0 
        
    ########################################
    ##              Fields             ##
    ########################################
    line_com_tx = fields.Integer(string='Com Tx (%)', required=True) # commission RATE
    line_com_HT = fields.Float(string='Com HT') # commission without taxes
    line_date_start = fields.Datetime(string='Du')
    line_date_end = fields.Datetime(string='Au')

    # section is a custom class defined below
    line_section = fields.Many2one('sale.order.section', string="Section")

    # permet la modif des BC
    name = fields.Text('Description', required=True, readonly=False) # something like  Air Tahiti Nui - TN 101 Los Angeles Papeete - Economy Class L 
    price_unit = fields.Float('Unit Price', required=True, digits_compute=dp.get_precision('Product Price'),
                               readonly=False) # 
    tax_id = fields.Many2many('account.tax', 'sale_order_tax', 'order_line_id', 'tax_id', 'Taxes', readonly=False) 
    product_uom_qty = fields.Float('Quantity', digits_compute=dp.get_precision('Product UoS'), required=True, readonly=False)
    product_uom = fields.Many2one('product.uom', 'Unit of Measure ', required=False)
    product_uos_qty = fields.Float('Quantity (UoS)', digits_compute=dp.get_precision('Product UoS'), readonly=False)
    discount = fields.Float('Discount (%)', digits_compute=dp.get_precision('Discount'), readonly=False)
    th_weight = fields.Float('Weight', readonly=False)
    
    ########################################
    ##              onChange              ##
    ########################################
    @api.one
    @api.onchange('line_com_tx')
    def on_change_line_com_tx(self):
        if self.line_com_tx:
            # update commission when the commission rate changes
            self.line_com_HT = self.line_com_tx * self.product_uom_qty * self.price_unit / 100.0
            
    @api.one
    @api.onchange('product_uom_qty')
    def on_change_product_uom_qty(self):
        if self.product_uom_qty:
            self.line_com_HT = self.line_com_tx * self.product_uom_qty * self.price_unit / 100.0
    
    @api.one
    @api.onchange('price_unit')
    def on_change_price_unit(self):
        if self.price_unit:
            self.line_com_HT = self.line_com_tx * self.product_uom_qty * self.price_unit / 100.0

    _defaults = {
        'sale_com_tx' : 20,
    }


class SaleOrderSection(models.Model):
    _name = 'sale.order.section'
    #_description = _(__doc__)
        
    name = fields.Char('Nom de la section', required=True)
    
    
# Devis
class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    # General info
    nb_ppl = fields.Integer(string="Nombres de personnes", required=True)
    nb_adult = fields.Integer(string="Nombre d'adultes", required=True)
    nb_child = fields.Integer(string="Nombre d'enfants", required=True)
    nb_baby= fields.Integer(string="Nombre de bébés", required=True)
    date_start = fields.Date(string="Départ")
    date_end = fields.Date(string="Retour")
    company_alt_id = fields.Many2one('res.company.alt', string="Agence") # company object
    
    customer_currency = fields.Many2one('res.currency', string='Devise client')
    total_currency = fields.Float('Total devise client', compute="_amount_customer_currency") # total amount due
    
    ########################### Fields computed using the same method #################################
    amount_com_ht = fields.Float(string="Total commissions HT", compute="_amount_com_ht", store=True)
    com_tva = fields.Float(
        string="Taux de TVA sur les commissions",
        default=lambda self: self._get_default_com_tva(),
        )
    amount_tva_com = fields.Float(string="Total TVA commissions", compute="_amount_com_ht")
    amount_vol_loc = fields.Float(string="Total vols domestiques", compute="_amount_com_ht")
    amount_vol_int = fields.Float(string="Total vols internationaux", compute="_amount_com_ht")
    amount_non_vol = fields.Float(string="Total hors vols", compute="_amount_com_ht")
    ####################################################################################################
    
    payment_ids = fields.One2many('sale.order.payment', 'order_id', string="Paiements")# payments performed by the customer
    solde = fields.Float(string="Reste à payer", compute="_amount_solde", store=True)
    
    #modification de order_line pour permettre l'édition des BC
    order_line = fields.One2many('sale.order.line', 'order_id', readonly=False, string='Order Lines', copy=True)


    # all the default values
    _defaults = {
        'nb_ppl' : 0,
        'nb_adult' : 0,
        'nb_child' : 0,
        'nb_baby' : 0,
    }
    
    @api.one
    @api.onchange('nb_adult')
    def on_change_nb_adult(self):
        if self.nb_adult:
            self.nb_ppl = self.nb_adult + self.nb_child + self.nb_baby
    
    @api.one
    @api.onchange('nb_child')
    def on_change_nb_child(self):
        if self.nb_child:
            self.nb_ppl = self.nb_adult + self.nb_child + self.nb_baby
    
    @api.one
    @api.onchange('nb_baby')
    def on_change_nb_baby(self):
        if self.nb_baby:
            self.nb_ppl = self.nb_adult + self.nb_child + self.nb_baby
            
    @api.one
    @api.onchange('customer_currency')
    def on_change_customer_currency(self):
        if self.customer_currency:
            tx = self.env['res.currency'].browse(self.customer_currency.id).rate_silent
            # on triche, les taux de changes sont calculer par rapport à l'euro
            self.total_currency = tx*self.amount_total/119.331742
            
    def _amount_customer_currency(self):
        if self.customer_currency:
            tx = self.env['res.currency'].browse(self.customer_currency.id).rate_silent
            # on triche, les taux de changes sont calculer par rapport à l'euro
            self.total_currency = tx*self.amount_total/119.331742
            
    def _get_default_com_tva(self):
        val = self.env["ir.config_parameter"].get_param("sale_tcv.com_TVA_setting")
        if val:
            tx = self.env['account.tax'].browse(int(val))
            if tx:
                ret = tx.amount
            else:
                ret = 0.13
        else:
            ret = 0.13
        return ret
    
    # Computes the total commission
    @api.depends('order_line','com_tva')
    def _amount_com_ht(self):
        # normal commission
        val = 0.0

        # commission for domestic flights
        val_dom = 0.0

        # commission for international flights
        val_int = 0.0

        #commission for non-flight stuff
        val_hors = 0.0

        # create all the sums
        for line in self.order_line:
            val += line.line_com_HT

            if line.product_id.categ_compta_int:
                val_int += (line.price_subtotal - line.line_com_HT - (line.line_com_HT * self.com_tva))
            elif line.product_id.categ_compta_loc:
                val_dom += (line.price_subtotal - line.line_com_HT - (line.line_com_HT * self.com_tva))
            else:
                val_hors += (line.price_subtotal - line.line_com_HT - (line.line_com_HT * self.com_tva))

        self.amount_com_ht=val
        self.amount_tva_com = self.com_tva * val
        self.amount_non_vol = val_hors
        self.amount_vol_int = val_int
        self.amount_vol_loc = val_dom
        
    # Amount that the customer still has to pay
    @api.depends('order_line','payment_ids')
    def _amount_solde(self):
        paid = 0
        
        for payment in self.payment_ids:
            if payment.is_paid:
                paid += payment.montant
        self.solde = self.amount_total - paid
        
    def print_quotation(self, cr, uid, ids, context=None):
        '''
        This function prints the sales order and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        #self.signal_workflow(cr, uid, ids, 'quotation_sent')
        return self.pool['report'].get_action(cr, uid, ids, 'sale_tcv.report_saleorder_tts', context=context)
            

class CrmLead(models.Model):
    _inherit = 'product.template'

    # Add category of flight     
    categ_compta_int = fields.Boolean(string="vol international")
    categ_compta_loc = fields.Boolean(string="vol local")

#### WTF 
class SaleOrderConfig(models.TransientModel):
    _inherit = 'sale.config.settings'
    
    com_TVA_setting = fields.Many2one("account.tax",string="Taux de TVA sur la commission")
    
    @api.model
    def get_default_com_TVA_setting(self, fields):
        #_logger.debug('Create a %s --------------------------------------------------', self._name)
        val = self.env["ir.config_parameter"].get_param(
            "sale_tcv.com_TVA_setting"
        )
        return {'com_TVA_setting': int(val)}
        #return val
        
       
    @api.one
    def set_com_TVA_setting(self):
        #_logger.debug('----- set ----- %s', self.com_TVA_setting)
        self.env["ir.config_parameter"].set_param(
            'sale_tcv.com_TVA_setting',
            self.com_TVA_setting.id
        )
 

# MODIFICATION DES TEMPLATE DE MAILS POUR RETIRER LES LIENS AUTO VERS ODOO
class FooterlessNotification(models.Model):
    _inherit = 'mail.notification'

    @api.model
    def get_signature_footer(self, user_id, res_model=None, res_id=None, context=None, user_signature=True):
        return ""

class mail_mail(models.Model):
    _inherit = 'mail.mail'

    def _get_partner_access_link(self, cr, uid, mail, partner=None, context=None):
        return None
