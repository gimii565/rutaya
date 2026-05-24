from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TelField, IntegerField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange

ASSOCIATIONS = [
    ('', 'Selecciona tu asociación'),
    ('ASOMOBI', 'ASOMOBI - Asociación de Mototaxistas del Beni'),
    ('AMOT', 'AMOT - Asociación de Mototaxistas Trinidad'),
    ('SINTRAMOT', 'SINTRAMOT - Sindicato de Mototaxistas'),
    ('ASMOT', 'ASMOT - Asociación de Mototaxistas'),
    ('FEDEMOT', 'FEDEMOT - Federación de Mototaxistas'),
    ('OTRA', 'Otra asociación'),
]

class RegisterForm(FlaskForm):
    name = StringField('Nombres', validators=[DataRequired(), Length(min=2, max=100)])
    paternal_lastname = StringField('Apellido paterno', validators=[DataRequired(), Length(min=2, max=50)])
    maternal_lastname = StringField('Apellido materno', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    phone = TelField('Teléfono / Celular', validators=[DataRequired(), Length(min=7, max=20)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('password', message='Las contraseñas no coinciden')])
    association_name = SelectField('Asociación de mototaxistas', choices=ASSOCIATIONS, validators=[DataRequired()])
    mototaxi_card = StringField('Número de carnet de mototaxista', validators=[DataRequired(), Length(min=3, max=50)])
    plate = StringField('Placa de la moto', validators=[DataRequired(), Length(min=5, max=20)])
    brand = StringField('Marca de la moto', validators=[DataRequired(), Length(min=2, max=50)])
    model = StringField('Modelo', validators=[DataRequired(), Length(min=1, max=50)])
    year = IntegerField('Año', validators=[DataRequired(), NumberRange(min=2000, max=2026)])
    color = StringField('Color', validators=[DataRequired(), Length(min=3, max=30)])
    submit = SubmitField('Registrarme como mototaxista')

class LoginForm(FlaskForm):
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Ingresar')

class AvailabilityForm(FlaskForm):
    is_available = BooleanField('Disponible para servicios')
    submit = SubmitField('Actualizar estado')