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

header to inherited viewPython

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

- mail_template_demo is the name of the module where the template resides
- browse is used to fetch the correct

### Creating email templates