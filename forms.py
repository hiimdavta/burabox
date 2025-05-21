from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TextAreaField, BooleanField, SubmitField, PasswordField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class ContactForm(FlaskForm):
    name = StringField('Név', validators=[DataRequired()])
    email = EmailField('E-mail cím', validators=[DataRequired(), Email()])
    subject = StringField('Tárgy', validators=[DataRequired()])
    message = TextAreaField('Üzenet', validators=[DataRequired()])
    privacy_agreement = BooleanField('Elfogadom az adatvédelmi nyilatkozatot', validators=[DataRequired()])
    submit = SubmitField('Küldés')

class ProfileForm(FlaskForm):
    name = StringField('Név', validators=[DataRequired()])
    email = EmailField('E-mail cím', validators=[DataRequired(), Email()])
    phone = StringField('Telefonszám')
    avatar = FileField('Profilkép')
    submit = SubmitField('Mentés')

class PasswordForm(FlaskForm):
    current_password = PasswordField('Jelenlegi jelszó', validators=[DataRequired()])
    new_password = PasswordField('Új jelszó', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Új jelszó megerősítése', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Jelszó módosítása') 