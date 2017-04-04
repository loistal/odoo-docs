# Recordsets
for record in records:
	record.write({"a": 1, "b": 2})
record in records
set1 | set2
records.filtered(lambda r: r.company_id == user.company_id)
records.sorted(key= lambda r: r.name)
records.mapped(lambda r: r.fields1 + r.fields2)
records.mapped("name")

# Environment (stores contextual data)
records.env.user
self.env["res.partner"].search([["is_company", "=", True]])

# Altering the environment
env["res.partner"].sudo().create({"name": "A partner"})

# Common ORM methods
self.create("name": "new name")
self.write("name": "new name")
self.browse([(4, 5, 7)])

if not record.exists():
	raise Exception("The record has been deleted")
records.ensure_one()

# Creating models
from openerp import models, fields 
class AModel(models.Model):
	_name = "a.model.name"

	field1 = fields.Char()
	a_field = fields.Char(default=compute_default_value)

	def compute_default_value(self):
		return self.get_value()

# Computed fields
from openerp import api
total = fields.Float(compute="_compute_total")
@api.depends("value", "tax")
def _compute_total(self):
	for record in self:
		record.total = record.value + record.value * record.tax
nickname = fields.Char(related="user_id.partner_id.name", store=True)

# onChange: update UI on the fly
@api.onchange("field1", "field2")
def check_change(self):
	if self.field1 < self.field2:
		self.field3 = True

<field name="name" on_change="0"/>

# Low level SQL
self.env.cr.execute("some_sql", param1, param2, param3)

# compatibility between old and new API
def old_method(self, cr, uid, ids, context=None):
	print ids
def new_method(self):
	self.old_method()
# Example education
env[model].browse([1, 2, 3, 4]).new_method()

# Environment swapping
r2 = records.with_context({}, key1 = True)

# Traditional style
model = self.pool.get(MODEL)
ids = model.serch(cr, uid, DOMAIN, context=context)
for rec in model.browse(cr, uid, ids, context=context):
	print rec.name 
model.write(cr, uid, ids, VALUES, context=context)

# record style
env = Environment(cr, uid, context)
model = env[MODEL]
recs = model.search(DOMAIN)
for rec in recs:
	print rec.name 
rec.write(VALUES)

# method with recordsets which are relevant
@api.multi

# methods wîth recordsets that do't matter
@api.model 

# specify the fields on which the compute method depends
@api.depends("partner_id.name")
def _compute_full_name(self)

# specify a constrain checker
@api.constrain("name", "description")
def _check_description(self):
	if self.name == self.description:
		raise ValidationError("Fields name must be different")

# returns an instance of the res.partner model
@returns("res.partner")

# self is exptected to be a singleton
@api.one 
def my_method(self, args):
	return self.name 

# field parameters
index "whether the field is indexed in the database"
groups = "restricts the field's access to the specified groups"
copy = "should the field be copied when the field is duplicated"

# parameters for computed fields
search = "name of the method which implements the search on the field"