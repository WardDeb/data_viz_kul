import marimo

__generated_with = "0.11.31"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import micropip
    return (micropip,)


@app.cell
async def _(micropip):
    await micropip.install(["svg-py", "pyarrow"])
    from svg import SVG, Circle, Line, Title, Text, Polygon, G, Path
    return Circle, G, Line, Path, Polygon, SVG, Text, Title


@app.cell
def _():
    import numpy as np
    import polars as pl
    import pandas as pd
    return np, pd, pl


@app.cell
def _():
    cat10_dic = {
        1: '#1f77b4',
        2: '#ff7f0e',
        3: '#2ca02c',
        4: '#d62728',
        5: '#9467bd',
        6: '#8c564b',
        7: '#e377c2',
        8: '#7f7f7f',
        9: '#bcbd22',
        10: '#17becf'
    }
    monthmap = {
        'dec': 12,
        'jan': 1,
        'feb': 2,
        'mar': 3
    }
    return cat10_dic, monthmap


@app.cell
def _(mo, pl):
    df = pl.read_csv(
        str(mo.notebook_location() / 'public/proper_events.csv')
    )
    df = df.with_columns(
        pl.col('start').str.strptime(pl.Datetime).alias('start'),
        pl.col('end').str.strptime(pl.Datetime).alias('end')
    )
    df
    return (df,)


@app.cell
def _():
    center_x = 400 # middle point of figure, in x
    center_y = 400 # middle point of figure, in y
    radius = 100
    return center_x, center_y, radius


@app.cell
def _(df):
    df.to_pandas()
    return


@app.cell
def _(
    Circle,
    Path,
    cat10_dic,
    center_x,
    center_y,
    df,
    month_selecter,
    monthmap,
    np,
    pd,
    pen_selecter,
    radius,
):
    # Densities

    _t = df.to_pandas()
    _t['month'] = _t['start'].dt.month
    _t = _t[
        (_t['station'] == pen_selecter.value) &
        (_t['month'] == monthmap[month_selecter.value])
    ]
    _k = _t['start'].dt.hour + _t['start'].dt.minute/60

    dens_elements = []
    pig_elements = []

    _hist, _bin_edges = np.histogram(_k, bins=200, density=True)
    _bin_centers = (_bin_edges[:-1] + _bin_edges[1:]) / 2
    _density_df = pd.DataFrame({
        'x': _bin_centers,
        'density': _hist
    })

    density = _density_df['density'].to_numpy()
    density = (density - density.min()) / (density.max() - density.min())

    path_data = ""
    for i, d in enumerate(density):
        _angle = (i / len(density)) * 2 * np.pi
        r = radius + d * 100
        x = center_x + r * np.cos(_angle)
        y = center_y + r * np.sin(_angle)
    
        if i == 0:
            path_data += f"M {x} {y} "
        else:
            path_data += f"L {x} {y} "
    path_data += f"L {center_x + radius} {center_y} Z"  # Close the path around the circle

    # Draw path
    dens_elements.append(Path(d=path_data, stroke='black', fill=cat10_dic[pen_selecter.value], opacity = 0.2))

    # circles per pig
    pigradius = {k: (i+1)*5 for i, k in enumerate(list(_t.value_counts('tattoo').index))}

    for i, r in _t.iterrows():
        _angle = (np.pi * 2 / 24) * r['start'].hour + r['start'].minute 
        _x = center_x + np.sin(_angle) * (radius + pigradius[r['tattoo']] + 100)
        _y = center_y + np.cos(_angle) * (radius + pigradius[r['tattoo']] + 100)
        pig_elements.append(
            Circle(cx = _x, cy = _y, r = 2, stroke='none', fill='black', opacity = 0.2)
        )
    return (
        d,
        dens_elements,
        density,
        i,
        path_data,
        pig_elements,
        pigradius,
        r,
        x,
        y,
    )


@app.cell
def _(Circle, Line, Text, center_x, center_y, np, radius):
    # Clock
    clock = []

    clock.append(
        Circle(cx = center_x, cy = center_y, r = radius, stroke='black', fill='white')
    )

    for hour in range(24):
        angle = (np.pi * 2 / 24) * hour 
        x1 = center_x + np.sin(angle) * (radius - 10)
        y1 = center_y - np.cos(angle) * (radius - 10)
        x2 = center_x + np.sin(angle) * radius
        y2 = center_y - np.cos(angle) * radius
        clock.append(
            Line(x1=x1, y1=y1, x2=x2, y2=y2, stroke='black')
        )

        # Add hour labels slightly inward
        label_x = center_x + np.sin(angle) * (radius - 25)
        label_y = center_y - np.cos(angle) * (radius - 25)
        clock.append(
            Text(text=str(hour), x=label_x, y=label_y, text_anchor="middle")
        )
    return angle, clock, hour, label_x, label_y, x1, x2, y1, y2


@app.cell
def _(df, mo, monthmap):
    pen_selecter = mo.ui.dropdown(
        options=df['station'].unique(),
        label="Select a pen.",
        allow_select_none = False,
        value='1'
    )
    month_selecter = mo.ui.dropdown(
        options=monthmap.keys(),
        label="Select a month.",
        allow_select_none = False,
        value='dec'
    )
    return month_selecter, pen_selecter


@app.cell
def _(pen_selecter):
    pen_selecter
    return


@app.cell
def _(month_selecter):
    month_selecter
    return


@app.cell
def _(SVG, clock, dens_elements, mo, pig_elements):
    # Define the SVG plot
    plot = SVG(
        width=800,
        height=800, 
        elements= dens_elements + clock + pig_elements
    )
    mo.Html(plot.as_str())
    return (plot,)


if __name__ == "__main__":
    app.run()
