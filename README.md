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