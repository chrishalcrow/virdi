from pynapple import load_file, Ts, TsGroup
import numpy as np

from .core import Session
import pandas as pd

class BriSession(Session):
    
    def __init__(self, session_data):
        Session.__init__(self, session_data)

    def load_clusters(session, cluster_id=None):

        path_to_data = session.get_data_path("clusters")

        sampling_frequency = 30_000

        spikes_df = pd.read_pickle(path_to_data)

        spikes_dict = dict(zip(spikes_df['cluster_id'].values, spikes_df['firing_times'].values))
        spikes_dict_s = {key: Ts(t=value/sampling_frequency) for key, value in spikes_dict.items()}
        spikes_frame = TsGroup(data=spikes_dict_s)

        if cluster_id is not None:
            return TsGroup({cluster_id: spikes_frame[cluster_id]})

        return spikes_frame
    

    def load_behavior(session):

        from pynapple import Tsd

        path_to_behaviour = session.get_data_path("beh")
        position_df = pd.read_pickle(path_to_behaviour)

        Px = Tsd(t=position_df['synced_time'].values, d=position_df['position_x'].values)
        Py = Tsd(t=position_df['synced_time'].values, d=position_df['position_y'].values)

        beh_dict = {'P_x': Px, 'P_y': Py}

        return beh_dict