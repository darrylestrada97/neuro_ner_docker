import os
import random
import string
import time
import shutil


def random_string(length):
    """Generate a random string of fixed length (lowercase letters)
    From https://pynative.com/python-generate-random-string/ """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


class  PharmaCoNERRunner:
    """Helper class to run PharmaCoNER"""
    def __init__(self, pharmaconer_path, output_path, parameters_path, ok_status_code='Data retrieved successfully.',
                 id_length=10,
                 clean_files=True):
        self.pharmaconer_path = pharmaconer_path
        self.venv_python_path = os.path.join(pharmaconer_path, 'bin', 'python')
        self.data_path = os.path.join(pharmaconer_path, 'data')
        self.output_path = output_path
        self.parameters_path = parameters_path
        self.ok_status_code = ok_status_code
        self.id_length = id_length
        self.clean_files = clean_files
        
        self.pretrained_model_folder = '/app/model'
        self.pharmaconer_base_command = "python" + ' ' + os.path.join(self.pharmaconer_path, 'src',
                                        'main.py') + ' --parameters_filepath ' + self.parameters_path \
                                        + ' --pretrained_model_folder ' + self.pretrained_model_folder +\
                                        ' --output_folder ' + output_path + ' --dataset_text_folder '
    def update_model(self, model_name):
        """Update model"""
        
        self.pretrained_model_folder = '/app/model'
        self.pharmaconer_base_command = "python" + ' ' + os.path.join(self.pharmaconer_path, 'src',
                                        'main.py') + ' --parameters_filepath ' + self.parameters_path \
                                        + ' --pretrained_model_folder ' + self.pretrained_model_folder +\
                                        ' --output_folder ' + self.output_path + ' --dataset_text_folder '

    def prepare_data(self, identifier, text):
        """Generate deploy set with the input text"""
        try:
            os.mkdir(os.path.join(self.data_path, identifier))
            os.mkdir(os.path.join(self.data_path, identifier, 'deploy'))
            with open(os.path.join(self.data_path, identifier, 'deploy', 'data.txt'), 'w') as f:
                f.write(text)
            return None
        except BaseException as error:
            return error

    def get_annotations(self, identifier, clean_files=True):
        """Get annotations from BRAT file output by PharmaCoNER"""
        filenames = os.listdir(self.output_path)
        found = False
        success = True
        for filename in filenames:
            if filename.startswith(identifier):
                found = True
                break
        if not found:
            return not success, 'Failed to get annotations'
        try:
            with open(os.path.join(self.output_path, filename, 'brat', 'deploy', 'data.ann'), 'r') as f:
                ann = f.read()
            if clean_files:
                shutil.rmtree(os.path.join(self.output_path, filename), ignore_errors=False, onerror=None)
                shutil.rmtree(os.path.join(self.data_path, identifier))
        except BaseException as error:
            return not success, 'Failed to clean tmp files: ' + str(error)
        return success, ann

    def ann_text_to_dict(self, annotations_text):
        """Build dictionary with annotations data from BRAT file"""
        brat = []
        for line in annotations_text.splitlines():
            entity = {}
            values = line.split()
            entity['id'] = values[0]
            entity['class'] = values[1]
            entity['start'] = int(values[2])
            entity['end'] = int(values[3])
            entity['entity'] = values[4]
            brat.append(entity)
        return brat

    def build_error_dict(self, error):
        """Build dictionary with error message"""
        status = error
        res = {'success': False, 'data': {}, 'message': status}
        return res

    def run(self, text,model_name=""):
        """Call PharmaCoNER and return dict with outputs"""
        time0 = time.time()
        identifier = random_string(self.id_length)
        error = self.prepare_data(identifier, text)
        self.model_name = model_name
        if error is not None:
            return self.build_error_dict(str('Failed to prepare data: ' + str(error)))
        command = self.pharmaconer_base_command + os.path.join(self.data_path, identifier) + ' --experiment_name ' +\
                  identifier
        try:
            os.chdir(os.path.join(self.pharmaconer_path, 'src'))
            os.system(command)
        except BaseException as error:
            return self.build_error_dict('Failed to run PharmaCoNER: ' + str(error))
        success, ann = self.get_annotations(identifier)
        if not success:
            return self.build_error_dict(ann)
        brat = self.ann_text_to_dict(ann)
        time1 = time.time()
        status = self.ok_status_code
        res = {'success': True, 'data': {'processing_time': str(time1 - time0), 'original_text': text, 'brat': brat},
               'message': status, 'timestamp': time1}
        return res


