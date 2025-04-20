import marimo

__generated_with = "0.12.9"
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
    import matplotlib
    import matplotlib.colors as mcolors
    return matplotlib, mcolors, np, pd, pl


@app.cell
def _(mo):
    mo.md(
        """
        <style>
          .tooltip-text {
            display: none;
            font-size: 12px;
            fill: black;  /* Tooltip text color */
            pointer-events: none;  /* Prevent the text from interfering with hover */
          }

          .my-circle:hover + .tooltip-text {
            display: block;
          }

          .my-circle:hover {
            fill: orange;
            cursor: pointer;
          }
        </style>
        """
    )
    return


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
def _(mo, np, pl):
    df = pl.read_csv(
        str(mo.notebook_location() / 'public/proper_events.csv')
    )
    df = df.with_columns(
        pl.col('start').str.strptime(pl.Datetime).alias('start'),
        pl.col('end').str.strptime(pl.Datetime).alias('end')
    )
    maxtime = np.ceil(((df.to_pandas()['end'] - df.to_pandas()['start']).dt.total_seconds() / 60).max())
    return df, maxtime


@app.cell
def _():
    center_x = 400 # middle point of figure, in x
    center_y = 400 # middle point of figure, in y
    radius = 100
    return center_x, center_y, radius


@app.cell
def _(df, pl):
    # Group and collect unique values
    grouped = df.group_by("station").agg(pl.col("tattoo").unique())
    pen_to_pig = dict(zip(grouped["station"], grouped["tattoo"]))
    return grouped, pen_to_pig


@app.cell
def _(
    Circle,
    Path,
    Text,
    cat10_dic,
    center_x,
    center_y,
    df,
    matplotlib,
    mcolors,
    np,
    pd,
    pen_selecter,
    pig_selecter,
    pig_spacing,
    radius,
):
    # Densities

    t = df.to_pandas()
    t['duration'] = (t['end'] - t['start']).dt.total_seconds() / 60

    t['month'] = t['start'].dt.month
    t = t[
        (t['station'] == pen_selecter.value)
        #(t['month'] == monthmap[month_selecter.value])
    ]
    circledf = t[
        (t['station'] == pen_selecter.value) &
        #(t['month'] == monthmap[month_selecter.value]) &
        (t['tattoo'].isin(pig_selecter.value))
    ]

    _k = t['start'].dt.hour + t['start'].dt.minute/60


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
    vc = circledf.value_counts('tattoo')
    norm = mcolors.Normalize(vmin=vc.min(), vmax=vc.max())
    cmap = matplotlib.colormaps["RdBu_r"]
    color_map = {
        item: mcolors.to_hex(cmap(norm(count)))  # cmap(norm(count)) returns RGBA, to_hex converts to hex
        for item, count in vc.items()
    }
    pigradius = {k: (i+1)*5*pig_spacing.value for i, k in enumerate(list(vc.index)[::-1])}

    for i, r in circledf.iterrows():
        _angle = (np.pi * 2 / 24) * r['start'].hour + r['start'].minute 
        _x = center_x + np.sin(_angle) * (radius + pigradius[r['tattoo']] + 100)
        _y = center_y + np.cos(_angle) * (radius + pigradius[r['tattoo']] + 100)
        pig_elements.append(
            Circle(
                cx = _x,
                cy = _y,
                r = r['duration'],
                stroke='none',
                fill=color_map[r['tattoo']],
                opacity = 0.2,
                class_="my-circle",
            )
        )
        pig_elements.append(
            Text(
                x = _x,
                y = _y,
                text=f"pen {r['station']}, pig {r['tattoo']}, duration = {round(r['duration'], 1)} mins",  
                class_="tooltip-text",
            )
        )
    return (
        circledf,
        cmap,
        color_map,
        d,
        dens_elements,
        density,
        i,
        norm,
        path_data,
        pig_elements,
        pigradius,
        r,
        t,
        vc,
        x,
        y,
    )


@app.cell
def _(Circle, Text, color_map, vc):
    color_legends = []

    _x = 50
    _y = 50
    for tattoo, count in list(vc.to_dict().items())[::-1]:
        color_legends.append(
            Circle(
                cx = _x,
                cy = _y,
                r = 5,
                stroke='none',
                fill=color_map[tattoo],
                opacity = 0.2
            )
        )
        color_legends.append(
            Text(
                x = _x + 50,
                y = _y,
                text=f"pig {tattoo}, total feeding events {count}",  
            )
        )
        _y += 50
    return color_legends, count, tattoo


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
def _(df, mo):
    pen_selecter = mo.ui.dropdown(
        options=df['station'].unique(),
        label="Select a pen.",
        allow_select_none = False,
        value='1'
    )
    pig_spacing = mo.ui.slider(
        start=1,
        stop=10,
        label="Pig spacing.",
        value=1
    )
    return pen_selecter, pig_spacing


@app.cell
def _(mo, pen_selecter, pen_to_pig):
    pig_selecter = mo.ui.multiselect(
        options=pen_to_pig[pen_selecter.value],
        label="Select pigs to visualize",
        value=[pen_to_pig[pen_selecter.value].to_list()[0]]
    )
    return (pig_selecter,)


@app.cell
def _(pen_selecter):
    pen_selecter
    return


@app.cell
def _(pig_spacing):
    pig_spacing
    return


@app.cell
def _(pig_selecter):
    pig_selecter
    return


@app.cell
def _(pig_selecter):
    print(f"Selected pigs = {' '.join(pig_selecter.value)}")
    return


@app.cell
def _(SVG, clock, dens_elements, mo, pig_elements):
    # Define the SVG plot
    plot = SVG(
        width=2000,
        height=1000, 
        elements= dens_elements + clock + pig_elements
    )
    mo.Html(plot.as_str())
    return (plot,)


@app.cell
def _(SVG, color_legends, mo):
     # Define the SVG plot
    plot_legends = SVG(
        width=600,
        height=1800, 
        elements= color_legends
    )
    mo.Html(plot_legends.as_str())
    return (plot_legends,)


if __name__ == "__main__":
    app.run()
