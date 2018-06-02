import glob
import scipy.io.wavfile

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
    for catalogue in glob.iglob('../small/*'):
        for vid in glob.glob(catalogue + '/*'):
            # i am not sure if all the recordings in id[0-9]{5}
            # belong to the same person
            parts  = glob.glob(vid + '/*.wav')
            if len(parts) > 3:
                data[id] = parts
            id += 1
    return data


def load_paths_if_same__person():
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
    paths = load_paths_if_same__person()
    train, test = split_paths(paths)
    train = load_data_contents(train, verbose)
    test = load_data_contents(test, verbose)
    return train, test


if __name__ == "__main__":
    train, test = get_data()
    print(train)
    print(test)