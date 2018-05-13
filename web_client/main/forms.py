from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from wtforms.validators import DataRequired


class Marsohod2Form(FlaskForm):
    project_name = StringField(_l("Project Name"), validators=[DataRequired()])
    ftdi = BooleanField(_l("FTDI"))
    clock = BooleanField(_l("Clock"))
    keys = BooleanField(_l("Keys"))
    sdram = BooleanField(_l("SDRAM"))
    leds = BooleanField(_l("Leds"))
    vga = BooleanField(_l("VGA"))
    adc = BooleanField(_l("ADC"))
    io = BooleanField(_l("I/O"))
    others = BooleanField(_l("Other"))
    submit = SubmitField(_l("Generate"))


class Marsohod2BForm(FlaskForm):
    project_name = StringField(_l("Project Name"), validators=[DataRequired()])
    ftdi = BooleanField(_l("FTDI"))
    clock = BooleanField(_l("Clock"))
    keys = BooleanField(_l("Keys"))
    sdram = BooleanField(_l("SDRAM"))
    leds = BooleanField(_l("Leds"))
    vga = BooleanField(_l("VGA"))
    adc = BooleanField(_l("ADC"))
    io = BooleanField(_l("I/O"))
    others = BooleanField(_l("Other"))
    submit = SubmitField(_l("Generate"))


class Marsohod3Form(FlaskForm):
    project_name = StringField(_l("Project Name"), validators=[DataRequired()])
    ftdi = BooleanField(_l("FTDI"))
    clock = BooleanField(_l("Clock"))
    keys = BooleanField(_l("Keys"))
    sdram = BooleanField(_l("SDRAM"))
    leds = BooleanField(_l("Leds"))
    tmds = BooleanField(_l("TMDS"))
    ftd = BooleanField(_l("FTD"))
    ftc = BooleanField(_l("FTC"))
    io = BooleanField(_l("I/O"))
    others = BooleanField(_l("Other"))
    submit = SubmitField(_l("Generate"))


class Marsohod3BForm(FlaskForm):
    project_name = StringField(_l("Project Name"), validators=[DataRequired()])
    ftdi = BooleanField(_l("FTDI"))
    clock = BooleanField(_l("Clock"))
    keys = BooleanField(_l("Keys"))
    sdram = BooleanField(_l("SDRAM"))
    leds = BooleanField(_l("Leds"))
    tmds = BooleanField(_l("TMDS"))
    ftd = BooleanField(_l("FTD"))
    ftc = BooleanField(_l("FTC"))
    io = BooleanField(_l("I/O"))
    others = BooleanField(_l("Other"))
    submit = SubmitField(_l("Generate"))


class DE1SoCForm(FlaskForm):
    project_name = StringField(_l("Project Name"), validators=[DataRequired()])
    audio = BooleanField(_l("Audio"))
    clock = BooleanField(_l("Clock"))
    i2c_for_audio_and_video_in = BooleanField(_l("I2C Audio and Video Input"))
    key = BooleanField(_l("Key"))
    adc = BooleanField(_l("ADC"))
    sdram = BooleanField(_l("SDRAM"))
    seg7 = BooleanField(_l("Seg7"))
    ir = BooleanField(_l("IR"))
    led = BooleanField(_l("Led"))
    ps2 = BooleanField(_l("PS2"))
    sw = BooleanField(_l("SW"))
    video_in = BooleanField(_l("Video Input"))
    vga = BooleanField(_l("VGA"))
    hps = BooleanField(_l("HPS"))
