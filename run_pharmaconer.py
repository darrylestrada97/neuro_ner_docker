import os
import random
import string
import time
import shutil
PHARMACONER_PATH = '/srv/PharmaCoNERTaggerDemo/PlanTL-PharmacoNER' # '/home/jordiae/Documents/PharmacoNERTask/FarmacoNER/src/CustomNeuroNER/'
VENV_PYTHON_PATH = os.path.join(PHARMACONER_PATH, 'bin', 'python')
DATA_PATH = os.path.join(PHARMACONER_PATH, 'data')
# OUTPUT_PATH = os.path.join(PHARMACONER_PATH, 'output')
OUTPUT_PATH = '/srv/PharmaCoNERTaggerDemo/demos_output' # '/home/jordiae/Documents/PharmacoNERTask/FarmacoNER/task/deploy_test_output2'
# PARAMETERS_PATH = 'pharmaconer_deploy_parameters.ini'
PARAMETERS_PATH = '/srv/PharmaCoNERTaggerDemo/PharmaCoNERDemoBackend/pharmaconer_deploy_parameters.ini'# os.path.join('/home/jordiae/PycharmProjects/PharmaCoNERDemoBackend', 'pharmaconer_deploy_parameters'
#                                                                                       '.ini')
PHARMACONER_COMMAND = VENV_PYTHON_PATH + ' ' + os.path.join(PHARMACONER_PATH, 'src', 'main.py') +\
                      ' --parameters_filepath ' + PARAMETERS_PATH + ' --dataset_text_folder '

sample_text = '''Presentamos el caso de una mujer de 70 años, con antecedentes de hipertensión arterial, hernia de 
hiato, estreñimiento e histerectomía que consultó por síndrome miccional irritativo desde hacía 8 meses, consistente 
en disuria y polaquiuria intensas con urgencias miccionales ocasionales sin otra sintomatología urológica añadida. En 
los últimos 6 meses había presentado 3 episodios de infección del tracto urinario bajo con urocultivos positivos a E. 
coli tratados por su médico de cabecera. El estudio inicial incluyó bioquímica sanguínea que fue normal, 
orina y estudio de sedimento de orina que mostraron intensa leucocituria, urocultivo que fue de nuevo positivo a 
E.coli y una citología urinaria por micción espontánea cuyo resultado fue células uroteliales sin atipias y 
abundantes leucocitos polimorfonucleares neutrófilos. Se prescribió tratamiento con antibioteparia y anticolinérgico 
(tolterodina). A los 3 meses la paciente fue revisada en consulta externa, persistiendo la sintomatología basada en 
disuria y polaquiuria, si bien había mejorado bastante de las urgencias con el anticolinérgico, e incluso días antes 
dela revisión había tenido nuevo episodio de infección urinaria. Ante la escasa respuesta encontrada, se inició un 
estudio más avanzado, solicitando urografía intravenosa para descartar tumor urotelial del tracto urinario superior, 
la cual fue rigurosamente normal, y ecografía urológica que también fue normal, por lo que se realizó cistoscopia en 
consulta, hallando lesiones nodulares, sobreelevadas, de aspecto sólido, discretamente enrojecidas, con áreas 
adyacentes de edema, localizadas en trígono y parte inferior de ambas caras laterales. Debido a este hallazgo, 
a pesar de que la paciente no tenía factores de riesgo para TBC y la urografía fue rigurosamente normal, se realizó 
baciloscopia en orina y cultivo Lowenstein-Jensen de 6 muestras de la primera orina de la mañana en días 
consecutivos, ya que las lesiones vesicales macroscópicamente podrían tratarse de tuberculomas, siendo estos estudios 
negativos para bacilo de Koch, por lo que se realizó resección endoscópica de las lesiones descritas bajo anestesia. 
El estudio anatomopatológico reveló ulceración de la mucosa con importante infiltrado inflamatorio crónico y 
congestión vascular, así como la presencia de células plasmáticas y linfocitos constituyendo folículos linfoids, 
los cuales están divididros en una zona central donde abundan linfoblastos e inmunoblastos, llamado centro 
germinativo claro, y una zona periférica formada por células maduras (linfocitos y células plasmáticas) dando lugar a 
los linfocitos del manto o corona radiada, como también se les denomina. 

A la paciente se le indicó medidas higiénico-dietéticas y profilaxis antibiótica mantenida ciclo largo a dosis única 
diaria nocturna 3 meses y posteriormente días alternos durante 6 meses con ciprofloxacino, vitamina A dosis única 
diaria 6 meses, prednisona 30mg durante 45 días y posteriormente en días alternos durante otros 45 días hasta su 
suspensión definitiva, y por último protección digestiva con omeprazol. La paciente experimentó clara mejoría con 
desaparición progresiva de la clínica, sobre todo a partir del tercer mes de tratamiento. Actualmente (al año de 
finalización del tratamiento), se encuentra asintomática con cistoscopia de control normal y urocultivos negativos. '''


def random_string(length=10):
    """Generate a random string of fixed length (lowercase letters)
    From https://pynative.com/python-generate-random-string/ """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def prepare_data(identifier, text):
    """Generate deploy set with the input text"""
    # text = sample_text
    try:
        os.mkdir(os.path.join(DATA_PATH, identifier))
        os.mkdir(os.path.join(DATA_PATH, identifier, 'deploy'))
        with open(os.path.join(DATA_PATH, identifier, 'deploy', 'data.txt'), 'w') as f:
            f.write(text)
        return None
    except BaseException as error:
        return error


def get_annotations(identifier):
    """Get annotations from BRAT file output by PharmaCoNER"""
    filenames = os.listdir(OUTPUT_PATH)
    found = False
    for filename in filenames:
        if filename.startswith(identifier):
            found = True
            break
    if not found:
        return 'Failed to get annotations'
    try:
        with open(os.path.join(OUTPUT_PATH, filename, 'brat', 'deploy', 'data.ann'), 'r') as f:
            ann = f.read()
        shutil.rmtree(os.path.join(OUTPUT_PATH, filename), ignore_errors=False, onerror=None)
        shutil.rmtree(os.path.join(DATA_PATH, identifier))
    except BaseException as error:
        return 'Failed to clean tmp files: ' + str(error)
    return ann


def run_pharmaconer(text):
    """Call PharmaCoNER"""
    time0 = time.time()
    identifier = random_string()
    error = prepare_data(identifier, text)
    if error is not None:
        return 'Failed to prepare data: ' + str(error)
    print('Running PharmaCoNER')
    command = PHARMACONER_COMMAND + os.path.join(DATA_PATH, identifier) + ' --experiment_name ' + identifier
    print(command)
    try:
        os.chdir(os.path.join(PHARMACONER_PATH, 'src'))
        os.system(command)
    except BaseException as error:
        return 'Failed to run PharmaCoNER: ' + str(error)
    ann = get_annotations(identifier)
    time1 = time.time()
    res = 'Tagged text in ' + str(time1-time0) + ' seconds:\n\n' + text + '\n\n' + ann
    return res
