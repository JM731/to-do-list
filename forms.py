from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateTimeLocalField, SelectField
from wtforms.validators import DataRequired
import pytz

TIMEZONES = pytz.all_timezones


class SignUpForm(FlaskForm):
    form_name = "sign_up_form"
    username = StringField(label="Username", validators=[DataRequired()], render_kw={"placeholder": "Username"})
    password = PasswordField(label="Password", validators=[DataRequired()], render_kw={"placeholder": "Password"})
    password2 = PasswordField(label="Re-enter password", validators=[DataRequired()],
                              render_kw={"placeholder": "Type your password again"})
    submit = SubmitField(label="Sign Up")


class LogInForm(FlaskForm):
    form_name = "log_in_form"
    username = StringField(label="Username", validators=[DataRequired()], render_kw={"placeholder": "Username"})
    password = PasswordField(label="Password", validators=[DataRequired()], render_kw={"placeholder": "Password"})
    submit = SubmitField(label="Log In")


class AddTaskForm(FlaskForm):
    task_name = StringField(validators=[DataRequired()], render_kw={"placeholder": "Task Name"})
    task_date = DateTimeLocalField(validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    submit = SubmitField(label="Add task", render_kw={"disabled": "disabled"})


class TimezoneForm(FlaskForm):
    timezone = SelectField('Timezone', choices=TIMEZONES, render_kw={"onchange": "checkSelectChange()"})
    change = SubmitField('Change timezone', render_kw={"disabled": "disabled"})
