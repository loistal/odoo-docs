# odoo-docs

## What is this?
This is a repository
consisting of notes from the Odoo documention.
The files are for reference purposes only and cannot be 
executed.

## Main documentation
This following section is my personnal reference.

### Creatign form buttons and actions
*http://www.odoo.yenthevg.com/category/odoo-8/buttons/* 

#### model and fields
from openerp import models, fields, api

```
class button_action_demo(models.Model):
    _name = 'button.demo'
    name = fields.Char(required=True,default='Click on generate name!')
    password = fields.Char()

<record model="ir.ui.view" id="view_buttons_form">
    <field name="name">Buttons</field>
    <field name="model">button.demo</field>
    <field name="type">form</field>
    <field name="arch" type="xml">
        <form string="Button record">
	    <!--The header tag is built to add buttons within. This puts them at the top -->
	    <header>
			<!--The oe_highlight class gives the button a red color when it is saved.
			It is usually used to indicate the expected behaviour. -->
		    <button string="Generate name" type="object" name="generate_record_name" class="oe_highlight"/>
			<button string="Generate password" type="object" name="generate_record_password"/>
			<button string="Clear data" type="object" name="clear_record_data"/>
	    </header>
	    <group>
			<field name="name"/>
			<field name="password"/>
	    </group>
	</form>
    </field>
</record>
```
- the type="object" in the buttons tells Odoo we want to trigger Python code 

#### Actions behind the buttons

```
@api.one
def generate_record_name(self):
    #Generates a random name between 9 and 15 characters long and writes it to the record.
    self.write({'name': ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(randint(9,15)))})
```
- write: updates the current record

### Finding and sending mail templates in Odoo
- How to find email templates
- How to call email templates
- How to send them to the user

#### Create the send email button

```
<odoo>
  <data>
      <record id="send_mail_partner_form_inherit" model="ir.ui.view">
        <field name="inherit_id" ref="base.view_partner_form"/>
        <field name="model">res.partner</field>
        <field name="arch" type="xml">
          <!-- Add a header with button to the existing view -->
          <xpath expr="//sheet" position="before">
              <header>
                <button name="send_mail_template" string="Send e-mail" type="object" class="oe_highlight"/>
              </header>
          </xpath>
        </field>
      </record>
  </data>
</odoo>

from odoo import models, fields, api
 
class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def send_mail_template(self):
        # Now let us find the e-mail template
        template = self.env.ref('mail_template_demo.example_email_template')
        # You can also find the e-mail template like this:
        # template = self.env['ir.model.data'].get_object('mail_template_demo', 'example_email_template')

        # Send the email
        self.env['mail.template'].browse(template.id).send_mail(self.id)

```

- mail_template_demo is the name of the module where the template resides
- browse is used to fetch the correct

### Creating email templates 	
- How to create tempaltes
- How to add it to the templates

#### dependencies

```
'depends': ['mail','contacts'],
```

#### Creating the email templates

```
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">

    </data>
</odoo>


  <record id="example_email_template" model="mail.template">
          <field name="name">Example e-mail template</field>
          <field name="email_from">${object.company_id and object.company_id.email or ''}</field>
          <field name="subject">Congratz ${object.name}</field>
          <field name="email_to">${object.email|safe}</field>
          <field name="lang">${object.lang}</field>
          <field name="model_id" ref="base.model_res_partner"/>
          <field name="auto_delete" eval="True"/>
		  <field name="body_html">
	              <![CDATA[
		          <p>Dear ${(object.name)},<br/><br/>
			  Good job, you've just created your first e-mail template!<br/></p>
	                  Regards,<br/>
	                  ${(object.company_id.name)}
		    ]]>
		  </field>
   </record>
```

#### Using Jinja2 variables for parsing email templates

- object is used to access all values from the existing model
- dynamic email template:

```
<field name="body_html">
              <![CDATA[
                %if object.website:
                  Because you have a website we might have a nice offer for you.<br/>
                  We can host your website ${object.website} for free if you sign up now.
                %endif
	      ]]>
	  
</field>
```


### xpath expressions
#### Creating new fields

```
from openerp import models, fields, api

class on_change_function(models.Model):
    #Inhertis the model product.template
    _inherit = 'product.template'
    #Creates two new fields (CostPrice and ShippingCost) in the model product.template
    CostPrice = fields.Float('Buy price')
    ShippingCost = fields.Float('Shipping Cost')
    FieldAfterGroup = fields.Char(string='Field After Group')
    FieldNewPage = fields.Char(string='Field New Page')
```

#### Inherit exhisting views

```
<record id="view_product_form_inherit" model="ir.ui.view">
  <field name="name">product.template.common.form.inherit</field>
  <field name="model">product.template</field>
  <field name="inherit_id" ref="product.product_template_form_view"/>
```

#### Xpath expressions

```
<xpath expr="//page[@string='Information']" position="after">
  <page name="Sample" string="Custom page">
    <group>
      <field name="FieldNewPage"/>
    </group>
  </page>
</xpath>
``` 
- In the Xpath:
	- page is the tag
	- @string is the string attribute of the page tag
- Another example
```
<xpath expr="//page[@string='Information']/group" position="after">
  <group>
    <field name="FieldAfterGroup"/>
  </group>
</xpath>
```
This creates a new group after the group which resides in the page tag.

### onchange event

- automatically updates a field when another field changes

```
from openerp import models, fields, api

class on_change_function(models.Model):
    #Inhertis the model product.template
    _inherit = 'product.template'
    #Creates two new fields (CostPrice and ShippingCost) in the model product.template
    CostPrice = fields.Float('Buy price')
    ShippingCost = fields.Float('Shipping Cost')

<field name="CostPrice" on_change="on_change_price(CostPrice,ShippingCost)"/>
<field name="ShippingCost" on_change="on_change_price(CostPrice,ShippingCost)"/>


    #This method will be called when either the field CostPrice or the field ShippingCost changes.
    def on_change_price(self,cr,user,ids,CostPrice,ShippingCost,context=None):
	#Calculate the total
	total = CostPrice + ShippingCost
        res = {
            'value': {
		#This sets the total price on the field standard_price.
                'standard_price': total
	      }
	}
	#Return the values to update it in the view.
	return res
```

### Set default value Many2one

'currency_id_invoices': fields.many2one('res.currency', string="Currency", required=True),

```
#This function automatically sets the currency to EUR.
    def _get_default_currency(self, cr, uid, context=None):
        res = self.pool.get('res.company').search(cr, uid, [('currency_id','=','EUR')], context=context)
        return res and res[0] or False

    #Default values that need to be set
    defaults = {
		'currency_id_invoices': _get_default_currency,
    }

```

### Logging


```
Importing Python loggerPython

#Import logger
import logging
#Get the logger
_logger = logging.getLogger(__name__)


```

### Automatically fill Many2many

```
class print_order_sample(models.Model):
    def _get_default_print_order_ids(self):
	cr = self.pool.cursor()
	self.env
		# Get all the records from the model
        return self.pool.get('sale.order.printorder').search(cr, self.env.uid, [])

    _inherit = 'sale.order'
    print_order_ids = fields.Many2many('sale.order.printorder','sale_order_print','print_id','order_print_id','Print order',help='This could be used to create a print order for your report, for example.',default=_get_default_print_order_ids)

#Another method consists in creating dummy records
<?xml version="1.0" encoding="utf-8"?>
<openerp>
    <data noupdate="1">
	<!--This will create some default records if they do not exist yet. We will always need these so these are auto-rendered. -->
        <record id="goals_print_order" model="sale.order.printorder">
            <field name="name">Goals</field>
        </record>
        <record id="workmethod_print_order" model="sale.order.printorder">
            <field name="name">Work method</field>
        </record>
        <record id="approach_print_order" model="sale.order.printorder">
            <field name="name">Approach</field>
        </record>
        <record id="orderlines_print_order" model="sale.order.printorder">
            <field name="name">Orderlines</field>
        </record>
        <record id="about_print_order" model="sale.order.printorder">
            <field name="name">About</field>
        </record>
        <record id="customer_print_order" model="sale.order.printorder">
            <field name="name">Customer</field>
        </record>
        <record id="references_print_order" model="sale.order.printorder">
            <field name="name">References</field>
        </record>
    </data>
</openerp>
```

### Creating and managing statusbars
- Show the progress that has been made
- create buttons that change the state of the statusbar

```
class statusbar(models.Model):
    _name = 'statusbar.demo'
    name = fields.Char('Name', required=True)
    """
    This selection field contains all the possible values for the statusbar.
    The first part is the database value, the second is the string that is showed. Example:
    ('finished','Done'). 'finished' is the database key and 'Done' the value shown to the user
    """
    state = fields.Selection([
            ('concept', 'Concept'),
            ('started', 'Started'),
            ('progress', 'In progress'),
            ('finished', 'Done'),
            ],default='concept')

<record model="ir.ui.view" id="view_statusbar_form">
    <field name="name">Statusbar</field>
    <field name="model">statusbar.demo</field>
    <field name="type">form</field>
    <field name="arch" type="xml">
	<form string="Workflow record">
	<!--The header tag is built to add buttons within. This puts them at the top -->
	<header>
	    <button string="Set to concept" type="object" name="concept_progressbar" attrs="{'invisible': [('state', '=', 'concept')]}"/>
	    <!--The oe_highlight class gives the button a red color when it is saved.
	    It is usually used to indicate the expected behaviour. -->
	    <button string="Set to started" type="object" name="started_progressbar" class="oe_highlight" attrs="{'invisible': [('state','!=','concept')]}"/>
	    <button string="In progress" type="object" name="progress_progressbar" attrs="{'invisible': [('state','=','progress')]}"/>
	    <button string="Done" type="object" name="done_progressbar" attrs="{'invisible': [('state','=','finished')]}"/>
	    <!--This will create the statusbar, thanks to the widget. -->
	    <field name="state" widget="statusbar"/>
	</header>
	<group>
	    <field name="name"/>
	</group>
        </form>
    </field>
</record>

#This function is triggered when the user clicks on the button 'Set to concept'
@api.one
def concept_progressbar(self):
    self.write({
        'state': 'concept',
    })

#This function is triggered when the user clicks on the button 'Set to started'
@api.one
def started_progressbar(self):
    self.write({
	'state': 'started'
    })

#This function is triggered when the user clicks on the button 'In progress'
@api.one
def progress_progressbar(self):
    self.write({
	'state': 'progress'
    })

#This function is triggered when the user clicks on the button 'Done'
@api.one
def done_progressbar(self):
    self.write({
	'state': 'finished',
    })
```
- Buttons allow to change the state
- the state widget allows to visualize the flow

### Creating automated actions / Schedulers


- in this example, we will create an automated action that runs every 2 minutes and loops over all the records from a certain model
- An important thing to note with automated actions is that they should always be defined within a noupdate field since this shouldn’t be updated when you update your module
```
class scheduler_demo(models.Model):
    _name = 'scheduler.demo'
    name = fields.Char(required=True)
    numberOfUpdates = fields.Integer('Number of updates', help='The number of times the scheduler has run and updated this field')
    lastModified = fields.Date('Last updated')

<?xml version="1.0" encoding="utf-8"?>
<openerp>
    <data noupdate="1">
        <record id="ir_cron_scheduler_demo_action" model="ir.cron">
            <field name="name">Demo scheduler</field>
            <field name="user_id" ref="base.user_root"/> <!-- user_id is a field of base.user_root -->
            <field name="interval_number">2</field>
            <field name="interval_type">minutes</field>
            <field name="numbercall">-1</field> <!-- -1 to run forever (10 to run for 10 minutes) -->
            <field eval="False" name="doall"/> <!-- False means that upon waking up the server after a period of downtime, the action should run and make up for that time -->
            <field eval="'scheduler.demo'" name="model"/>
            <field eval="'process_demo_scheduler_queue'" name="function"/>
        </record>
   </data>
</openerp>

class scheduler_demo(models.Model):
    _name = 'scheduler.demo'
    name = fields.Char(required=True)
    numberOfUpdates = fields.Integer('Number of updates', help='The number of times the scheduler has run and updated this field')
    lastModified = fields.Date('Last updated')

    #This function is called when the scheduler goes off
    def process_demo_scheduler_queue(self, cr, uid, context=None):


    #This function is called when the scheduler goes off
    def process_demo_scheduler_queue(self, cr, uid, context=None):
	
	scheduler_line_obj = self.pool.get('scheduler.demo')
	
	#Contains all ids for the model scheduler.demo
  	scheduler_line_ids = self.pool.get('scheduler.demo').search(cr, uid, [])   
	
	#Loops over every record in the model scheduler.demo
        for scheduler_line_id in scheduler_line_ids :
	   		#Contains all details from the record in the variable scheduler_line
            scheduler_line =scheduler_line_obj.browse(cr, uid,scheduler_line_id ,context=context)
	    	numberOfUpdates = scheduler_line.numberOfUpdates
	    	#Prints out the name of every record.
            _logger.info('line: ' + scheduler_line.name)
	    	#Update the record
	    	scheduler_line_obj.write(cr, uid, scheduler_line_id, {'numberOfUpdates': (numberOfUpdates +1), 'lastModified': datetime.date.today()}, context=context)

```

### Inheriting and modifying QWeb reports

- to inherit, you must know the module and the id of the original report
- the correct report to inherit from is the one whose name and id end with "document"

```
<!-- Inherit quotation report (from module sale) -->
<template id="report_quotation_inherit_demo" inherit_id="sale.report_saleorder_document">
	<!-- Finds the first table with as class table table-condensed and gives the ability to modify it
	This will replace everything withing tr (including tr)-->
	<xpath expr="//table[@class='table table-condensed']//thead//tr" position="replace">
	    <tr style="background-color:lightgray;">
	        <th>Description</th>
	        <th class="text-right">Price</th>
	    </tr>
	</xpath>
	<xpath expr="//tbody[@class='sale_tbody']//tr//td[4]" position="replace">
	</xpath>
	<xpath expr="//tbody[@class='sale_tbody']//tr//td[3]" position="replace">
	</xpath>
	<xpath expr="//tbody[@class='sale_tbody']//tr//td[2]" position="replace">
	</xpath>
</template>
```

- add the original module to the dependencies of the custom module
```
'depends': ['sale'],
```

#### Reference


#### General
- external_layout_ adds the default header and footer 
- the report content is inside of the <div class="page">
- all fields of the docs objects can be received by the template

#### In-report variables
- docs: records for the current report
- doc-ids: list of ids for the docs records
- doc-model: model for the docs records
- time: reference to the standards Python library time
- user: record for the user printing the report
- company: record for the current user's company

#### Miscellanous
- twitter and font awesome classes can be used in the template
- can insert CSS locally
- global CSS can be inserted this way:

```
<template id="report_saleorder_style" inherit_id="report.style">
  <xpath expr=".">
    <t>
      .example-css-class {
        background-color: red;
      }
    </t>
  </xpath>
</template>
```

### QWeb

- template engine 
- template dirctives prefixed by t-
- the <t> tag isn't rendered:

```
<t t-if="condition">
    <p>Test</p>
</t>
```

#### Data output
- use esc

```
<p><t t-esc="value"/></p>
```

#### Output

- t-foreach: provides the collection to iterate on
- t-as: provides the designation of the current element

```
<t t-foreach="[1, 2, 3]" t-as="i">
    <p><t t-esc="i"/></p>
</t>

# RESULTS IN
<p>1</p>
<p>2</p>
<p>3</p>

# Alternative
<p t-foreach="[1, 2, 3]" t-as="i">
    <t t-esc="i"/>
</p>

```

#### Variables on i

- the index of a foreach loop has several variables:
	- i_all: the object being iterated over
	- i_value: current iteration value (i provides the key)
	- ...
- can set custom variables:

```
<p t-foreach="[1, 2, 3]" t-as="i">
    <t t-set="existing_variable" t-value="True"/>
    <t t-set="new_variable" t-value="True"/>
    <!-- existing_variable and new_variable now True -->
</p>
```

#### Attributes (aka weird stuff)


*Note:* $name is the name of the aatribute

- t-attf-$name: used to mix strings and non-literal expressions:

```
<t t-foreach="[1, 2, 3]" t-as="item">
    <li t-attf-class="row {{ item_parity }}"><t t-esc="item"/></li>
</t>

# RENDERED AS 
<li class="row even">1</li>
<li class="row odd">2</li>
<li class="row even">3</li>
```

- t-att-$name:

```
<div t-att-a="42"/>
# RENDERED AS 
<div a="42"></div>

<div t-att="{'a': 1, 'b': 2}"/>
# RENDERED AS 
<div a="1" b="2"></div>

<div t-att="['a', 'b']"/>
# RENDERED AS 
<div a="b"></div>

``` 	

#### Setting variables

```
<t t-set="foo" t-value="2 + 1"/>
<t t-esc="foo"/>
```

#### Calling sub-templates

- allows reuse

```
<t t-call="other-template"/>
```

- content set inside of the t-call is evaluated before rendering the sub-template

```
<t t-call="other-template">
    <t t-set="var" t-value="1"/>
</t>
```

#### Template inheritance

- use t-extend

```
<t t-extend="base.template">
    <t t-jquery="ul" t-operation="append">
        <li>new element</li>
    </t>
</t>
```

#### debugging

- t-log:

```
<t t-set="foo" t-value="42"/>
<t t-log="foo"/>
```

- t-js

```
<t t-set="foo" t-value="42"/>
<t t-js="ctx">
    console.log("Foo is", ctx.foo);
</t>
```