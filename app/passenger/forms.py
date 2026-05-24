from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TelField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegisterForm(FlaskForm):
    name = StringField('Nombre completo', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    phone = TelField('Teléfono', validators=[DataRequired(), Length(min=7, max=20)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('password', message='Las contraseñas no coinciden')])
    submit = SubmitField('Registrarse')

class LoginForm(FlaskForm):
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Ingresar')

class RequestTripForm(FlaskForm):
    origin = StringField('Origen', validators=[DataRequired(), Length(min=3, max=200)])
    destination = StringField('Destino', validators=[DataRequired(), Length(min=3, max=200)])
    submit = SubmitField('Solicitar Taxi')