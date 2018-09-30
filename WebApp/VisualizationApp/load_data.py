import glob
import scipy.io.wavfile
import numpy as np

def load_old_data(mode='train'):
    """
    loads small data set from train or test directories
    returns a list of tuples of sample rate and signal
    i'th tuple in train corresponds to i'th tuple in test
    """
    data = []
    for path in glob.iglob('../' + mode + '/*.wav'):
        sample_rate, signal = scipy.io.wavfile.read(path)
        data.append((sample_rate, signal))
    return data



def load_paths():
    """
    loads data from a part of set extracted from yt
    :return dict of form {vid_id, [list of paths to videos]}:
    """
    id = 0
    data = {}
    for catalogue in glob.iglob('smallDataSet/*'):
        for vid in glob.glob(catalogue + '/*'):
            # i am not sure if all the recordings in id[0-9]{5}
            # belong to the same person
            parts  = glob.glob(vid + '/*.wav')
            if len(parts) > 3:
                data[id] = parts
            id += 1
    return data


def load_paths_if_same_person():
    """
    loads data from a part of set extracted from yt
    :return dict of form {person_id, [list of paths to videos]}:
    """
    id = 0
    data = {}
    for catalogue in glob.iglob('../small/*'):
        data[id] = []
        for vid in glob.glob(catalogue + '/*'):
            parts  = glob.glob(vid + '/*.wav')
            data[id] += parts
        id += 1
    return data

def split_paths(data):
    """
    splits the data in train and test collections
    by default the data is divided in 3 : 1 proportion
    :return train and test collections:
    """
    test, train = {}, {}
    for id, paths in data.items():
        train[id] = paths[:3*len(paths)//4]
        test[id] = paths[3*len(paths)//4:]
    return train, test


def load_files_contents(path_list, verbose=False):
    """
    loads vaw file as sample rate, signal
    from list of paths of files
    :param path_list:
    :return:
    """
    files = []
    for path in path_list:
        if type(path) == int:
            if verbose:
                print('incorrect path')
        else:
            if verbose:
                print('loading file: {}'.format(path))
            files.append(scipy.io.wavfile.read(path))
    return files


def load_files_contents_generator(path_list, verbose=False):
    """
    creates generator to read files,
    from list of paths of files
    this approach saves memory
    :param path_list:
    :return:
    """
    for path in path_list:
        if type(path) == int:
            if verbose:
                print('incorrect path')
        else:
            if verbose:
                print('loading file: {}'.format(path))
            yield scipy.io.wavfile.read(path)



def load_data_contents(paths_dict, verbose=False):
    for id in paths_dict:
        paths_dict[id] = load_files_contents(paths_dict[id], verbose)
    return paths_dict


def get_data(verbose=False):
    """
    loads data for further processing
    :return train and test data dicts:
    """
    paths = load_paths_if_same_person()
    train, test = split_paths(paths)
    train = load_data_contents(train, verbose)
    test = load_data_contents(test, verbose)
    return train, test

def load_raw_file(file_name):
	return scipy.io.wavfile.read('./VisualizationApp/smallDataSet/' + file_name + '.wav')

def load_file(file_name, relative_window_width):
	sample_rate, file = load_raw_file(file_name)
	window_width =  len(file) // (sample_rate * relative_window_width)
	return [np.mean(file[k * window_width:(k + 1) * window_width]) for k in range(len(file) // window_width)]

def get_file_names():
	from os import listdir
	file_names = listdir('./VisualizationApp/smallDataSet')
	return [file_name.split('.')[0] for file_name in file_names]

if __name__ == "__main__":
	print(get_file_names())