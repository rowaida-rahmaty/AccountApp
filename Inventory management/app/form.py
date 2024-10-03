from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, IntegerField,TextAreaField, SelectField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange, Length

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),Length(min=8, message='Password must be at least 8 characters long.')])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Sign Up')

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    description = StringField('Product Description', validators=[DataRequired()])
    cost = DecimalField('cost', places=2, validators=[DataRequired(), NumberRange(min=0)])
    price = DecimalField('Price', places=2, validators=[DataRequired(), NumberRange(min=0)])
    quantity = IntegerField('Quantity')
    reorder_level = IntegerField('Reorder Level', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Add Product')

class ProductEditForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    cost = DecimalField('cost', places=2, validators=[DataRequired(), NumberRange(min=0)])# added 
    price = DecimalField('Price', places=2, validators=[DataRequired(), NumberRange(min=0)])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)], render_kw={'readonly': True}) #disabled since I don't want users to change the quantity randomly without a transaction happening 
    reorder_level = IntegerField('Reorder Level', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Update Product')

class RecordPurchaseForm(FlaskForm):
    product_id = SelectField('Product',choices=[], coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity Purchased', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Record Purchase')

class RecordSaleForm(FlaskForm):
    product_id = SelectField('Product', choices=[], coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity Sold', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Record Sale')


