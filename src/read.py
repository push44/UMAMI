import pickle
import pandas as pd
import numpy as np
    
def read(schema_file, data_file):
    """
    Reads schema file and data file to generate content dataframe
    """
    with open(schema_file, "rb") as file:
        # List of 39 dictionaries each with keys name, type, baseType
        schema = pickle.load(file)
    with open(data_file, "rb") as file:
        # List of lists with shape 1987 x 39
        data = pickle.load(file)
        data = np.array(data)

    schema_names = list(map(lambda dictionary: dictionary["name"], schema))
    
    content = {}
    for ind, name in enumerate(schema_names):
        content[name] = list(data[:, ind])

    return pd.DataFrame(content)
