from pynapple import load_file, Ts, TsGroup
import numpy as np

from .core import Session
import pandas as pd

class BriSession(Session):
    
    def __init__(self, session_data, mouse, date, session_type):
        Session.__init__(self, session_data)
        self.mouse = mouse
        self.date = date
        self.session_type = session_type

    def load_clusters(session, cluster_id=None):

        if (clusters := session.cache.get('clusters')) is not None:
            if cluster_id is None:
                return clusters
            else:
                return clusters[cluster_id]
        
        path_to_data = session.get_data_path("clusters")

        sampling_frequency = 30_000

        spikes_df = pd.read_pickle(path_to_data)

        spikes_dict = dict(zip(spikes_df['cluster_id'].values, spikes_df['firing_times'].values))
        spikes_dict_s = {key: Ts(t=value/sampling_frequency) for key, value in spikes_dict.items()}
        spikes_frame = TsGroup(data=spikes_dict_s)

        session.cache['clusters'] = spikes_frame

        if cluster_id is not None:
            return TsGroup({cluster_id: spikes_frame[cluster_id]})

        return spikes_frame
    
    def get_cluster_ids(session):
        clusters = session.load_clusters()
        return clusters.index

    def load_position(session):

        if (positions := session.cache.get('positions')) is not None:
            return positions

        from pynapple import Tsd

        path_to_behaviour = session.get_data_path("position")
        position_df = pd.read_pickle(path_to_behaviour)

        Px = Tsd(t=position_df['synced_time'].values, d=position_df['position_x'].values)
        Py = Tsd(t=position_df['synced_time'].values, d=position_df['position_y'].values)

        beh_dict = {'P_x': Px, 'P_y': Py}

        session.cache['positions'] = positions

        return beh_dict
    
    def load_object_position(session):

        import polars as pl

        path_to_object_position = session.get_data_path("object_position")
        all_object_positions = pl.scan_csv(path_to_object_position)

        object_positions = all_object_positions.filter(
            pl.col("mouse") == int(session.mouse),
            pl.col('date') == session.date,
            pl.col('session') == session.session_type,
        ).select(['object_position_x', 'object_position_y'])

        return object_positions.collect().to_numpy()[0]
    


