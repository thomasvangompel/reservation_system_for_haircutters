from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DecimalField, IntegerField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class ReservationForm(FlaskForm):
    customer_name = StringField('Your Name', validators=[DataRequired(), Length(max=80)])
    customer_email = StringField('Your Email', validators=[Email(), Length(max=120)])
    customer_phone = StringField('Your Phone Number', validators=[Length(max=20)])
    skill_id = StringField('Skill')
    block = StringField('Block', validators=[DataRequired()])
    submit = SubmitField('Reserve')

class ProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=80)])
    store_name = StringField('Store Name', validators=[Length(max=80)])
    email = StringField('Email', validators=[Email(), Length(max=120)])
    street = StringField('Street', validators=[Length(max=120)])
    postal_code = StringField('Postal Code', validators=[Length(max=20)])
    city = StringField('City', validators=[Length(max=80)])
    country = StringField('Country', validators=[Length(max=80)])
    submit = SubmitField('Save Profile')

class SkillForm(FlaskForm):
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('x', 'Other / All')], validators=[DataRequired()])
    type = StringField('Type', validators=[DataRequired(), Length(max=80)])
    price = DecimalField('Price (€)', validators=[DataRequired()])
    duration = IntegerField('Duration', validators=[DataRequired()])
    image = FileField('Example Image', validators=[DataRequired()])
    submit = SubmitField('Add Skill')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class WerknemerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[DataRequired()])
    submit = SubmitField('Add Employee')

class CustomerForm(FlaskForm):
    name = StringField('Customer Name', validators=[DataRequired(), Length(max=80)])
    phone = StringField('Phone', validators=[Length(max=20)])
    email = StringField('Email', validators=[Email(), Length(max=120)])
    submit = SubmitField('Add Customer')
