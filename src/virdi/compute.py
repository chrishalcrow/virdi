from pynapple import compute_2d_tuning_curves, TsGroup, load_file
import numpy as np
from spatial_manifolds.util import gaussian_filter_nan
import matplotlib.pyplot as plt


def compute_rate_map(session, cluster_id, minmax=None):

    beh = session.load_behavior()
    spikes = session.load_clusters()

    P_x, P_y = beh['P_x'], beh['P_y']

    if minmax is None:
        tc = compute_2d_tuning_curves(
            TsGroup([spikes[cluster_id]]),
            np.stack([P_x, P_y], axis=1),
            nb_bins=(40,40),
            # range=bin_config["bounds"],
            # epochs=session["moving"].intersect(epochs),
        )[0][0]
    else:
        tc = compute_2d_tuning_curves(
            TsGroup([spikes[cluster_id]]),
            np.stack([P_x, P_y], axis=1),
            nb_bins=(40,40),
            minmax=minmax,
            # range=bin_config["bounds"],
            # epochs=session["moving"].intersect(epochs),
        )[0][0]

    return tc

def plot_rate_map(session, cluster_id, sigma=2.5, minmax=None):

    tc = compute_rate_map(session, cluster_id=cluster_id, minmax=minmax)
    smooth_tc = gaussian_filter_nan(tc, [sigma,sigma])

    fig, ax = plt.subplots()
    ax.imshow(smooth_tc)

    return fig
