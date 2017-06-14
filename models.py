from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import StringField, SelectField, FileField, HiddenField
from wtforms.validators import AnyOf, DataRequired, Length
from wtforms.widgets import TextArea

VOICES = [
          ('Joanna', 'Joanna (Female, US English)'),
          ('Mizuki', 'Mizuki (Female, Japanese)'),
          ('Filiz', 'Filiz (Female, Turkish)'),
          ('Astrid', 'Astrid (Female, Swedish)'),
          ('Maxim', 'Maxim (Male, Russian)'),
          ('Tatyana', 'Tatyana (Female, Russian)'),
          ('Carmen', 'Carmen (Female, Romanian)'),
          ('Ines', 'Inês (Female, Portuguese)'),
          ('Cristiano', 'Cristiano (Male, Portuguese)'),
          ('Vitoria', 'Vitória (Female, Brazilian Portuguese)'),
          ('Ricardo', 'Ricardo (Male, Brazilian Portuguese)'),
          ('Maja', 'Maja (Female, Polish)'),
          ('Jan', 'Jan (Male, Polish)'),
          ('Ewa', 'Ewa (Female, Polish)'),
          ('Ruben', 'Ruben (Male, Dutch)'),
          ('Lotte', 'Lotte (Female, Dutch)'),
          ('Liv', 'Liv (Female, Norwegian)'),
          ('Giorgio', 'Giorgio (Male, Italian)'),
          ('Carla', 'Carla (Female, Italian)'),
          ('Karl', 'Karl (Male, Icelandic)'),
          ('Dora', 'Dóra (Female, Icelandic)'),
          ('Mathieu', 'Mathieu (Male, French)'),
          ('Celine', 'Céline (Female, French)'),
          ('Chantal', 'Chantal (Female, Canadian French)'),
          ('Penelope', 'Penélope (Female, US Spanish)'),
          ('Miguel', 'Miguel (Male, US Spanish)'),
          ('Enrique', 'Enrique (Male, Castilian Spanish)'),
          ('Conchita', 'Conchita (Female, Castilian Spanish)'),
          ('Geraint', 'Geraint (Male, Welsh English)'),
          ('Salli', 'Salli (Female, US English)'),
          ('Kimberly', 'Kimberly (Female, US English)'),
          ('Kendra', 'Kendra (Female, US English)'),
          ('Justin', 'Justin (Male, US English)'),
          ('Joey', 'Joey (Male, US English)'),
          ('Ivy', 'Ivy (Female, US English)'),
          ('Raveena', 'Raveena (Female, Indian English)'),
          ('Emma', 'Emma (Female, British English)'),
          ('Brian', 'Brian (Male, British English)'),
          ('Amy', 'Amy (Female, British English)'),
          ('Russell', 'Russell (Male, Australian English)'),
          ('Nicole', 'Nicole (Female, Australian English)'),
          ('Vicki', 'Vicki (Female, German)'),
          ('Marlene', 'Marlene (Female, German)'),
          ('Hans', 'Hans (Male, German)'),
          ('Naja', 'Naja (Female, Danish)'),
          ('Mads', 'Mads (Male, Danish)'),
          ('Gwyneth', 'Gwyneth (Female, Welsh)'),
          ('Jacek', 'Jacek (Male, Polish)')
         ]

VOICE_IDS = [
             'Joanna', 'Mizuki', 'Filiz', 'Astrid', 'Maxim', 'Tatyana',
             'Carmen', 'Ines', 'Cristiano', 'Vitoria', 'Ricardo', 'Maja',
             'Jan', 'Ewa', 'Ruben', 'Lotte', 'Liv', 'Giorgio', 'Carla', 'Karl',
             'Dora', 'Mathieu', 'Celine', 'Chantal', 'Penelope', 'Miguel',
             'Enrique', 'Conchita', 'Geraint', 'Salli', 'Kimberly', 'Kendra',
             'Justin', 'Joey', 'Ivy', 'Raveena', 'Emma', 'Brian', 'Amy',
             'Russell', 'Nicole', 'Vicki', 'Marlene', 'Hans', 'Naja', 'Mads',
             'Gwyneth', 'Jacek'
            ]

AUDIO_FORMATS = ['ogg_vorbis', 'mp3', 'pcm']

class PollyForm(FlaskForm):
    voiceId = SelectField('Voice', choices=VOICES,
                          validators=[AnyOf(VOICE_IDS)])
    text = StringField('Text', widget=TextArea(),
                       validators=[DataRequired(), Length(max=500)])
    output_format = HiddenField('Output Format',
                                validators=[AnyOf(AUDIO_FORMATS)])


class TestForm(FlaskForm):
    test_voiceId = SelectField('Voice', choices=VOICES,
                               validators=[AnyOf(VOICE_IDS)])
    test_text = StringField('Text', widget=TextArea(),
                            validators=[DataRequired(), Length(max=500)])
    file = FileField('Upload', validators=[
                                           FileRequired(),
                                           FileAllowed(['wav','ogg'],
                                                       'WAV or OGG required.')
                                          ])
