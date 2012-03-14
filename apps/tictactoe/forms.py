from wtforms import Form, TextField, validators

class EmailForm(Form):
    email = TextField("Email", [validators.Email])

