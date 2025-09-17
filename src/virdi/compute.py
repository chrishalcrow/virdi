from pynapple import compute_2d_tuning_curves, TsGroup, load_file
import numpy as np
from spatial_manifolds.util import gaussian_filter_nan
import matplotlib.pyplot as plt
from virdi.bri import BriSession
import pynapple as nap

def compute_rate_map(session, cluster_id, minmax=None):

    position = session.load_position()
    spikes = session.load_clusters()

    P_x, P_y = position['P_x'], position['P_y']

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

    tc = np.transpose(tc[:,::-1])

    return tc

def plot_rate_map(session: BriSession, cluster_id, sigma=2.5, minmax=None, plot_object=False, object_position=None):

    tc = compute_rate_map(session, cluster_id=cluster_id, minmax=minmax)
    smooth_tc = gaussian_filter_nan(tc, [sigma,sigma])

    fig, ax = plt.subplots()
    ax.imshow(smooth_tc, extent=(0, 100, 0, 100))

    ax.set_xlabel("x-Position (cm)")
    ax.set_ylabel("y-Position (cm)")

    ax.set_title(f"Rate map: {session.mouse}, {session.date}, {session.session_type}.")

    if plot_object is True or object_position is not None:
        if object_position is None:
            object_position = session.load_object_position()
        #if not np.all(object_position):
        ax.scatter(object_position[0], object_position[1], s=50, c='red')
        from matplotlib.patches import Circle
        center = object_position
        radius = 18
        circle = Circle(center, radius, fill=False, color='red')
        ax.add_patch(circle)

    return fig


def plot_spikes_on_trajectory(session, cluster_id, highlight_spike=None):

    cluster_df = session.load_clusters(cluster_id=cluster_id)[cluster_id]
    P_x, P_y = session.load_position().values()

    fig, ax = plt.subplots()

    ax.plot(P_x, P_y, color='black', linewidth=2, zorder=1, alpha=0.7)

    P_x_at_spikes = P_x.interpolate(cluster_df)
    P_y_at_spikes = P_y.interpolate(cluster_df)

    ax.scatter(P_x_at_spikes, P_y_at_spikes, color='red', marker='o', s=10, zorder=2)
    if highlight_spike is not None:
        ax.scatter(P_x_at_spikes[highlight_spike], P_y_at_spikes[highlight_spike], color='green', marker='o', s=40, zorder=2)

    return fig


def plot_occupancy(session, bins=20):

    P_x, P_y = session.load_position().values()
    occupancy_map = np.histogram2d(P_x.values, P_y.values, bins=bins)[0]
    occupancy_map = np.transpose(occupancy_map[:,::-1])

    fig, ax = plt.subplots()

    occupancy_ax = ax.imshow(occupancy_map, cmap='Blues')
    fig.colorbar(occupancy_ax)

    return fig


def plot_video_frame(session, frame=0):

    import cv2

    video_path = session.get_data_path('video')

    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
    _, frame = cap.read()

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    fig, ax = plt.subplots()

    ax.imshow(frame_rgb[::-1,120:600])
    ax.set_xticks([0,120,240,360,480],[0,25,50,75,100])
    ax.set_yticks([0,120,240,360,480],[100,75,50,25,0])

    return fig


def compute_spikes_near_object_ratio(session, object_position, cluster_id, mask_cm=18):

    spikes = session.load_clusters(cluster_id=cluster_id)[cluster_id]
    Px, Py = session.load_position().values()
    near_object = (np.sqrt(np.pow(Px.values - object_position[0],2) + np.pow(Py.values - object_position[1],2)) < mask_cm)
    
    is_near_object = nap.Tsd(t=Px.times(), d=near_object)
    #mouse_near_object = np.sum(is_near_object.values)/np.shape(is_near_object.values)

    spike_near_object = spikes.value_from(is_near_object)
    #spiking_near_object = np.sum(spike_near_object.values)/np.shape(spike_near_object.values)

    return np.sum(spike_near_object.values)/np.sum(is_near_object.values)
    #return (spiking_near_object/mouse_near_object)[0]


def compute_object_spike_ratios(bri_experiment, mouse, date, cluster_id, session_types=None, mask_cm=18, object_position=None):

    if session_types is None:
        session_types = bri_experiment.get_sessions(mouse, date)

    sessions = [bri_experiment.load_session(mouse, date, session=session_type) for session_type in session_types]
    
    if object_position is None:
        object_position = sessions[1].load_object_position()

    ratios = []
    for session in sessions:
        ratios.append(compute_spikes_near_object_ratio(session, object_position, cluster_id, mask_cm=mask_cm))

    return dict(zip(session_types,ratios))

def compute_two_session_object_score(bri_experiment, mouse, date, cluster_id, session_types, mask_cm=18):
    """
    Always make obj be second!!!
    Returns a p-value. Big means more likely to be object!
    """

    from scipy.stats import norm

    object_position = bri_experiment.load_session(mouse, date, 'obj').load_object_position()
    
    object_positions = [np.array([object_position[0], object_position[1]])]
    while len(object_positions) < 20:
        x = (np.random.rand()*0.8 + 0.1)*100
        y = (np.random.rand()*0.8 + 0.1)*100
        if np.sqrt(np.pow(object_position[0] - x, 2) + np.pow(object_position[1] - y, 2)) > 1.5*mask_cm:
            object_positions.append(np.array([x,y]))

    ratios = np.array([list(compute_object_spike_ratios(
            bri_experiment, 
            mouse, 
            date, 
            cluster_id=cluster_id, 
            session_types=session_types, 
            object_position=pretend_object_position
        ).values()) for pretend_object_position in object_positions])

    means = np.mean(ratios, axis=1)
    ders = (ratios[:,1] - ratios[:,0])/means
    p_value = norm.cdf(ders[0], np.mean(ders), np.std(ders))

    return p_value