# Import Form and RecaptchaField (optional)
from flask_wtf import FlaskForm # , RecaptchaField
from flask_wtf.file import FileField, MultipleFileField, FileAllowed, FileRequired

# Import Form elements such as TextField and BooleanField (optional)
from wtforms import BooleanField, IntegerField, StringField, TextAreaField, SelectField, \
     PasswordField, HiddenField, SubmitField, DateField, validators # BooleanField

# Import Form validators
from wtforms.validators import Email, EqualTo, ValidationError


from app.main_page_module.p_objects.artifact import Artifact

from datetime import datetime


#email verification
import re
import os.path


class ArtifactForm(FlaskForm):
    # z_<type>_<num>
    col_ref_num = HiddenField('col_ref_num', [validators.InputRequired(message='Dont fiddle around with the code!')])
    
    name = StringField('Naziv', [validators.InputRequired(message='We need a title.'), validators.Length(max=150)])
    
    type_ = SelectField('Tip:', [
        validators.InputRequired(message='You need to specify the type')], 
                         choices=[])
    
    
    period = SelectField('Obdobje:', [
        validators.InputRequired(message='You need to specify the type')], 
                         choices=[])    
    
    
    state_entity = StringField('Politicna Entiteta', [validators.Length(max=150)])
    replica = SelectField(u'Replika:', [
        validators.InputRequired(message='You need to specify the time')], 
                         choices=[('1', 'Da'), ('0', 'Ne')])
        
    provenance_notes = TextAreaField('Opombe o izvoru')
    owners = StringField('Lastniki, CSV', [validators.Length(max=300)])
    description = TextAreaField('Opis')   
    historical_context = TextAreaField('Zgodovinski kontekst')   
        
    buy_price = IntegerField('Cena ob nakupu', [validators.InputRequired(message='Cena je zahtevana')], default=0)    
    sold_price = IntegerField('Cena ob prodaji', default=0)    
        
    joined_collection_in_year = IntegerField('Leto prejema v kolekcijo', [validators.InputRequired(message='Letnica je zahtevana')], default=datetime.now().year)    
    left_collection_in_year = IntegerField('Leto oddaje iz kolekcije', default=0)    
        
    reference = StringField('Reference', [validators.Length(max=150)], default="")
        
    public = SelectField(u'Javno vidno', [
        validators.InputRequired(message='You need to specify the time')], 
                         choices=[('0', 'Ne'), ('1', 'Da')])      
        
        
    curr_location_of_item = StringField('Trenutna lokacija artifakta', [validators.Length(max=150)])
    
    coin_type = StringField('Tip kovanca', [validators.Length(max=150)])
    coin_description = TextAreaField('Opis kovanca')  
    ruler = StringField('Vladar, pod katerim je bila kovanec izdan', [validators.Length(max=150)])
    mint_city = StringField('Mesto kovnice', [validators.Length(max=100)])
    mint_period = StringField('Leto/obdobje kovanja', [validators.Length(max=50)])
    material = StringField('Material', [validators.Length(max=150)])
    weight = StringField('Teža', [validators.Length(max=50)])
    diameter = StringField('Premer', [validators.Length(max=50)])
    
    obverse = TextAreaField('Obverse - Lice')   
    reverse = TextAreaField('Reverse - Hrbet')   
    
    grade = SelectField(u'Ocena Stanja', [
        validators.InputRequired(message='You need to specify the time')], 
                         choices=[])          
    
    image = FileField("Slika", validators=[
                FileAllowed(["PNG", "png", "JPG", "jpg", "JPEG", "jpeg"], "Only .png .jpeg and jpg allowed")])         
    
    
    submit = SubmitField('Dodaj Artifakt')
    
    
    def __init__(self, *args, **kwargs):
        super(ArtifactForm, self).__init__(*args, **kwargs)
        self.type_.choices = [[id_, name] for name, id_ in Artifact.types().items()]  
        self.period.choices = [[data_[0], name] for name, data_ in Artifact.periods().items()]       
        self.grade.choices = [[id_, name] for name, id_ in Artifact.grades().items()]        


class LoginForm(FlaskForm):
    username_or_email = StringField('Username or Email', [validators.InputRequired(message='Forgot your email address?')])
    password = PasswordField('Password', [validators.InputRequired(message='Must provide a password.')])
    remember = BooleanField()
    
    submit = SubmitField('Login')


 
form_dicts = {"Artifact": ArtifactForm,
              "Login": LoginForm
              } 
