from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DecimalField, \
    MultipleFileField, SelectField, FloatField, HiddenField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Length
from app import images

from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    psw = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    psw = PasswordField('Password', validators=[DataRequired(), Length(4,24)])
    psw2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('psw')])
    submit = SubmitField('Register')

    #Cridat automaticament pel WTForms per validar el camp username (validate_<field_name>)
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already exists, please use a different username.')

#Cambia el ',' per '.' d'un numero float
class MyFloatField(FloatField):
    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = float(valuelist[0].replace(',','.'))
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid float value'))

class AddAdForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    choices = [('All', 'All'), ('Books', 'Books'), ('Cars', 'Cars'), ('Flats','Flats'),('Toys', 'Toys'),('Others', 'Others')]
    category = SelectField("Category", choices=choices,validators=[DataRequired()])
    price = MyFloatField("Price", validators=[DataRequired()])
    images = MultipleFileField("Images", validators=[FileAllowed(images, 'Images only!')])
    submit = SubmitField('Add')

    def validate_price(self, price):
        if price.data > 1000000.0 or price.data < 0.01:
            raise ValidationError('Min: 0.01€, Max: 1.000.000€')

    def validate_images(selfself, images):
        print(images.data)


class SearchForm(FlaskForm):
    search_field = StringField("Search", validators=[DataRequired()])
    price_min = MyFloatField("Min. Price", validators=[DataRequired()], default=0.01)
    price_max = MyFloatField("Max. Price", validators=[DataRequired()], default=1000000.0)
    choices = [('All', 'All'), ('Toys', 'Toys'), ('Books', 'Books')]
    category = SelectField("Category", choices=choices, validators=[DataRequired()], default='All')
    submit = SubmitField("Search")

    def validate(self):
        if not FlaskForm.validate(self): #Doing default validation
            return False

        if self.price_min.data > 1000000.0 or self.price_min.data < 0.01:
            self.price_min.errors.append('Min. Price >= 0.01 and Min.Price <= 1.000.000')
            return False
        if self.price_max.data > 1000000.0 or self.price_max.data < 0.01:
            self.price_max.errors.append('Max. Price >= 0.01 and Max.Price <= 1.000.000')
            return False
        if self.price_min.data > self.price_max.data:
            self.price_max.errors.append('Min. Price must be < Max. Price')
        return True

