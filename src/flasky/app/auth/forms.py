from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from flasky.app.models import User


class LoginForm(FlaskForm):
    email = StringField("Email",
                        validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Log In")


class RegistrationForm(FlaskForm):
    email = StringField("Email", validators=[
        DataRequired(), Length(1, 64), Email()])
    username = StringField("Username", validators=[
        DataRequired(), Length(1, 64),
        Regexp("^[A-Za-z][A-Za-z0-9_.]*$", 0, "Usernames must have only letters, digits, . or _")
    ])
    password = PasswordField("Password", validators=[
        DataRequired(), EqualTo("password2", message="Passwords must match")])
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email already registered.")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Username already in use.")


class ChangePasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[
        DataRequired(), EqualTo("new_password2", message="Passwords must match")])
    new_password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Update Password")


class PasswordResetRequestForm(FlaskForm):
    """ Form is used by an user to request a password reset."""
    email = StringField("Email", validators=[
        DataRequired(), Length(1, 64), Email()])
    submit = SubmitField("Reset Password")


class PasswordResetForm(FlaskForm):
    """ Form used to reset the password. """
    new_password = PasswordField("New Password", validators=[
        DataRequired(), EqualTo("new_password2", message="Passwords must match")])
    new_password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Reset Password")


class ChangeEmailForm(FlaskForm):
    email = StringField("New Email", validators=[
        DataRequired(), Length(1, 64), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Update Email Address")
