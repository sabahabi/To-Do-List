from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class AddTasksForm(FlaskForm):
    task_name = StringField("Enter New Task ", validators=[DataRequired()])
    submit = SubmitField("Add task", render_kw={'class': 'btn btn-secondary'})
class EditTasksForm(FlaskForm):
    task_name=StringField("Edit Task", validators=[DataRequired()])
    submit = SubmitField("Edit", render_kw={'class': 'btn btn-secondary'})