import os
import shutil


class Writer:
    def __init__(self, target_file, environment):
        self.target_file = target_file
        self.environment = environment

    def write(self):
        shutil.copy(self.target_file, f'{self.target_file}.backup')

        with open(self.target_file, 'w') as f:
            f.seek(0)
            for k, v in self.environment.items():
                f.write(f'{k.upper()}={v}\n')

        os.remove(f'{self.target_file}.backup')
