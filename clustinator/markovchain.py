'''
@author: An Dang, Henning Schulz
'''

import numpy as np
import pandas as pd
from sklearn import preprocessing
from scipy.sparse import csr_matrix


class MarkovChain:

    def __init__(self, sessions, states):
        self.sessions = sessions
        self.states = states

    def encoding_factorize(self, session_value):
        """
        Label encoding the data and return factorize session value.
        :return: Factorize session value
        """
        le = preprocessing.LabelEncoder()
        le.fit(session_value)
        le.transform(session_value)

        return pd.factorize(session_value)[0]

    def markov_chain(self, encoding_factorize):
        """
        Compute a markov chain from the session, the matrix is as big as the session.
        :param encoding_factorize: Need the factorize session
        :return: the probability matrix
        """
        num_states = 1 + max(encoding_factorize)
        matrix = [[0] * num_states for _ in range(num_states)]

        for (i, j) in zip(encoding_factorize, encoding_factorize[1:]):
            matrix[i][j] += 1

        for row in matrix:
            s = sum(row)
            if s > 0:
                row[:] = [f / s for f in row]
        
        matrix[num_states - 1][num_states - 1] = 1

        return matrix

    def transition_matrix(self, value, matrix):
        """
        Transfer the matrix into a Markov chain with implementing the states.
        :param value: values from the the raw session
        :param matrix: the compute matrix from the session
        :return: return a flatten vector of the matrix
        """
        # unique array in the right order
        value = np.array(value)
        _, idx = np.unique(value, return_index=True)

        df = pd.DataFrame(data=matrix, index=value[np.sort(idx)],
                          columns=value[np.sort(idx)])

        df_1 = pd.DataFrame(index=self.states, columns=self.states, dtype='float64').assign(**{'$': 1.0})
        df_1.update(df, join='left')
        df_1 = df_1.fillna(0)

        return np.array(df_1.values.flatten().tolist())

    def csr_sparse_matrix(self):
        """
        Convert the flatten markov chain into a csr sparse matrix
        :return: csr sparse matrix for the clustering and sessinID
        """
        markovchains = []
        session_ids = []

        for key, value in self.sessions.items():
            # add initial and final state
            value.insert(0, "INITIAL*")
            value.append("$")
            
            encoding = self.encoding_factorize(value)

            matrix = self.markov_chain(encoding)

            transition_matrix = self.transition_matrix(value, matrix)

            markovchains.append(transition_matrix)

            session_ids.append(key)

        return csr_matrix(markovchains), session_ids