from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.crud import get_user_by_username, get_user_by_email

class LoginForm(FlaskForm):
    """Form for user login."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class RegistrationForm(FlaskForm):
    """Form for user registration."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    def validate_username(self, username):
        """Check if username already exists."""
        user = get_user_by_username(username.data)
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        """Check if email already exists."""
        user = get_user_by_email(email.data)
        if user:
            raise ValidationError('Email already exists. Please use a different one.')

class ItemForm(FlaskForm):
    """Form for creating and editing items."""
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    category_id = SelectField('Category', coerce=int, validators=[])
    tag_ids = SelectMultipleField('Tags', coerce=int, validators=[])

    def __init__(self, *args, **kwargs):
        """Initialize the form with dynamic choices."""
        super(ItemForm, self).__init__(*args, **kwargs)
        
        # Leave the field optional if no categories exist
        self.category_id.validators = []
        
        # Set choices to None initially - they'll be set in the route
        self.category_id.choices = []
        self.tag_ids.choices = []

class CategoryForm(FlaskForm):
    """Form for creating and editing categories."""
    name = StringField('Name', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Description')

class TagForm(FlaskForm):
    """Form for creating tags."""
    name = StringField('Name', validators=[DataRequired(), Length(max=30)])

class UserProfileForm(FlaskForm):
    """Form for editing user profile."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    current_password = PasswordField('Current Password')
    new_password = PasswordField('New Password')
    confirm_password = PasswordField('Confirm New Password', validators=[EqualTo('new_password')])