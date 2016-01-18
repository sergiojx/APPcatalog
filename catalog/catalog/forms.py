from wtforms import Form, IntegerField, BooleanField, TextField, TextAreaField, PasswordField, RadioField, DateTimeField, SelectField, validators


class NewCategory(Form):
	name = TextField('Name', [validators.Required(),validators.Length(min=4, max=25, message='name error')])
	description = TextField('Description', [validators.Required()])
	user_id = IntegerField('User_id', [validators.Required()])
	
	
class NewItem(Form):
	name = TextField('Name', [validators.Required()])
	description = TextAreaField('Description', [validators.Required()])
	imageurl = TextField('Image URL', [validators.Required()])
	categorySelect = SelectField(u'Category',coerce=int)
	
	

