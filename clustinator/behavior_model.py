'''
@author: Henning Schulz
'''

from elastic_connection import ElasticBehaviorConnection

class BehaviorModel:
    
    # TODO: just load it right in the beginning, then get the endpoints, then pass the label encoder and transform to 1d array
    
    def __init__(self, app_id, tailoring, interval_start):
        self.json = ElasticBehaviorConnection(app_id, tailoring, interval_start).get_latest()
    
    def get_endpoints(self):
        """
        Extracts and returns the endpoints contained in this behavior model.
        :return: The endpoints (will NOT contain $ or INITIAL*)
        """
        
        states = set()
        
        for markov_chain in self.json['markov-chains']:
            for from_state in markov_chain['transitions'].keys():
                if from_state not in [ '$', 'INITIAL*' ]:
                    states.add(from_state)
        
        return list(states)
    
    def _load_chain(self, json, label_encoder):
        num_states = len(label_encoder.classes_)
        transitions = json['transitions']
        array = [0] * (num_states ** 2)
        
        for from_state in transitions.keys():
            for to_state in transitions[from_state].keys():
                prob = transitions[from_state][to_state]['probability']
                from_idx = label_encoder.transform([from_state])[0]
                to_idx = label_encoder.transform([to_state])[0]
                array[from_idx * num_states + to_idx] = prob
        
        return array
    
    def as_1d_dict(self, label_encoder):
        """
        Returns the loaded behavior model as a dict of 1d arrays, one per Markov chain.
        The order of the Markov states corresponds to the label encoder.
        The keys are the Markov chain IDs (string).
        :param label_encoder: Label encoder to use for getting the index per state.
        :return: A dict { 'markov chain id' -> [1d array] }
        """
        
        if self.json is None:
            return None
        
        dict_1d = dict()
            
        for markov_chain in self.json['markov-chains']:
            array_1d = self._load_chain(markov_chain, label_encoder)
            dict_1d[markov_chain['id']] = array_1d
        
        return dict_1d
