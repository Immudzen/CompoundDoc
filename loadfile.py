def objectLoadFile(path):
    import pickle
    file = open(path, 'r')
    p = pickle.Unpickler(file)
    object = p.load()
    file.close()
    return object
