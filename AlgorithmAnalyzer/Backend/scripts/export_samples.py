"""
This script servs to export samples from database.
Usage:
    python export_samples.py --path=path_to_existing_direcotry --type=type_of_samples

All samples will be exported in the format:
    username1/
        train/
            1.wav
            2.wav
            labels.txt
        test/
            1.wav
            labels.txt
    username2/
        train/
            1.wav
            labels.txt
        text/
        ... etc
Where labels file indicates if samples are real or fake. Example:
    labels.txt:
        1.wav   0
        2.wav   1
        3.wav   1
here 1 means thatsample is genuine and 0 that it's fake.
"""

import argparse
import os
from pathlib import Path

os.sys.path.append('..')
from config import BaseConfig   # noqa

VALID_TYPES = ['wav']


class NotDirectoryException(Exception):
    def __init__(self, path):
        super().__init__()
        self.path = path

    def __str__(self):
        return f'self.path is not a valid directory path!'


class BadSampleTypeException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message

    def __str__(self):
        return f'{self.message} is not a valid type.'


def directory(path):
    if os.path.isdir(path):
        return path
    else:
        raise NotDirectoryException(path)


def sample_type(string):
    if string not in VALID_TYPES:
        raise BadSampleTypeException(string)
    else:
        return string


parser = argparse.ArgumentParser(
    description="Export samples from database.",
    usage="pipenv shell && python export_samples.py --path=<path to directory to export to>"
)
parser.add_argument(
    '--path',
    help='Path to directory to which samples should be copied.',
    type=directory
)
parser.add_argument(
    '--type',
    help=f'String representing sample_type to extract. Allowed are {VALID_TYPES}.',
    type=sample_type
)

args = parser.parse_args()

sample_manager = BaseConfig.SAMPLE_MANAGER

for purpose in ['train', 'test']:
    samples, labels = sample_manager.get_all_samples(purpose=purpose, multilabel=False, sample_type=args.type)
    for user in samples:
        base_path = Path(args.path)
        path = base_path.joinpath(f'{user}/{purpose}')
        path.mkdir(parents=True, exist_ok=True)
        labels_str = ''

        for i, sample in enumerate(samples[user]):
            with open(path.joinpath(f'{i}.{args.type}'), 'wb') as f:
                f.write(sample.read())

            labels_str += f'{i}.{args.type}\t{labels[user][i]}\n'

        with open(path.joinpath('labels.txt'), 'w') as labels_file:
                labels_file.write(labels_str)
