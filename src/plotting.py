import matplotlib.pyplot as plt
import numpy as np
plt.rcParams['axes.spines.right'] = False
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['lines.linewidth'] = 1.5
plt.rcParams['xtick.direction'] = "in"
plt.rcParams['ytick.direction'] = "in"
plt.rcParams['legend.frameon'] = False
import inspect



def simple_plot(arr1, arr2):
    
    # Get caller local variables for name lookup
    fig = plt.figure(figsize=(5, 2))

    caller_locals = inspect.currentframe().f_back.f_locals
    # Find names by matching objects
    arr1_name = next((name for name, val in caller_locals.items() if val is arr1), 'arr1')
    arr2_name = next((name for name, val in caller_locals.items() if val is arr2), 'arr2')
    plt.plot(arr1,arr2)
    
    if "_"  in arr1_name:   
        arr1_name = arr1_name.replace("_", r"_{")
        arr1_name+=r"}"

    if "_"  in arr2_name:   
        arr2_name = arr2_name.replace("_", r"_{")
        arr2_name+=r"}"
        
    plt.xlabel(rf"${arr1_name}$")
    plt.ylabel(rf"${arr2_name}$")
    plt.tight_layout()
    plt.show()



def multi_plot(*args, xlabel="x", ylabel="y",zero='true'):
    # args[0] is x data
    x = args[0]

    # Get caller local variables for name lookup
    caller_locals = inspect.currentframe().f_back.f_locals

    fig = plt.figure(figsize=(5.1, 3.5))

    # Loop over all y arrays passed after x
    for a in args[1:]:
        # Find the first variable name in caller locals whose value is this object
        arr_name = next((name for name, val in caller_locals.items() if val is a), None)
        if arr_name is None:
            arr_name = 'data'

        # Replace underscores with LaTeX subscript
        if "_" in arr_name:
            arr_name = arr_name.replace("_", r"_{") + r"}"

        plt.plot(x, a, label=fr"${arr_name}$", alpha=0.7)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.plot(x,np.zeros_like(x),':k')
    plt.legend()
    plt.tight_layout()
    plt.show()




def plotly_3d(x, y, z, title="", name="", marker_size=3, line_color='blue', line_width=4, marker_color=None, colorscale='Peach', fig=None):
    """
    Generic 3D plotter for data in x, y, z arrays.
    If fig is provided, adds a new line to the existing figure.
    """
    import plotly.graph_objects as go

    if marker_color is None:
        marker_color = np.arange(len(x))

    trace = go.Scatter3d(
        x=x, y=y, z=z,
        mode='lines+markers',
        marker=dict(size=marker_size, color=marker_color, colorscale=colorscale),
        line=dict(color=line_color, width=line_width),
        name=name
    )

    if fig is None:
        fig = go.Figure(data=[trace])
        fig.update_layout(
            title=title,
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Z'
            ),
            margin=dict(l=0, r=0, b=0, t=30)
        )
    else:
        fig.add_trace(trace)
        # Optionally update title if provided
        if title:
            fig.update_layout(title=title)

    return fig

def plot_vector(x,y,z,fig, name="",arrowsize=1.0):

    import plotly.graph_objects as go
        # End-to-end vector components
    u = x[-1] - x[0]
    v = y[-1] - y[0]
    w = z[-1] - z[0]

    # Add the line segment (shaft of the vector)
    fig.add_trace(go.Scatter3d(
        x=[x[0], x[-1]],
        y=[y[0], y[-1]],
        z=[z[0], z[-1]],
        mode='lines',
        line=dict(color='red', width=6),
        name=name
    ))

    # Add the arrowhead using a cone
    fig.add_trace(go.Cone(
        x=[x[-1]], y=[y[-1]], z=[z[-1]],
        u=[u], v=[v], w=[w],
        sizemode="absolute",
        sizeref=arrowsize,  # adjust to control size of the arrowhead
        anchor="tip",
        colorscale=[[0, 'red'], [1, 'red']],
        showscale=False,
    ))
    return fig


