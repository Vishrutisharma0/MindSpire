from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField,SubmitField,PasswordField
from wtforms.validators import InputRequired, Email,Length, EqualTo

class BlogForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired()], render_kw={"placeholder": "Enter the title"})
    post = TextAreaField("Text", validators=[InputRequired()], render_kw={"placeholder": "Enter the blog post"})
    submit1=SubmitField("Save")
    submit2=SubmitField("Share")

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])

    password = PasswordField("Password",validators=[InputRequired(),Length(min=4,max=20,message="Your password must be between 4 and 20 characters long.",),
        ],
    )

    confirm_password = PasswordField( "Confirm Password",validators=[InputRequired(), EqualTo( "password",message="This password did not match the one in the password field.",
            ),
        ],
    )
    submit1 = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit1 = SubmitField("Login")
