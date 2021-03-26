from scipy import sparse
from scipy.spatial import distance

from scipy.sparse import load_npz
import os

vectors_path = "code/model_serialization/vectors/"

m_joint = None

varieties = ["AR", "ES", "CO", "CU", "MX", "PE", "VE"]

matrices = os.listdir(vectors_path)
matrices = [f for f in matrices if f.startswith("matrix_")]

for variety in varieties:
    for file in matrices:
        current_matrix = load_npz(vectors_path + file)
        if file.__contains__(variety):
            if m_joint == None:
                m_joint = current_matrix
            else:
                m_joint += current_matrix
    sparse.save_npz(vectors_path + "matrix_all_" + variety + ".npz", m_joint)