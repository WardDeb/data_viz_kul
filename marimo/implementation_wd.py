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
def _(mo):
    mo.md(
        r"""
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
async def _(micropip):
    await micropip.install(["svg-py", "pyarrow"])
    from svg import SVG, Circle, Line, Title, Text, Polygon, G
    return Circle, G, Line, Polygon, SVG, Text, Title


@app.cell
def _():
    import numpy as np
    import polars as pl
    import pandas as pd
    return np, pd, pl


@app.cell
def dt_to_linear():
    def dt_to_linear(df):
        _df = df.to_pandas()
        dt_dow = _df['start'].dt.dayofweek
        dt_hour = _df['start'].dt.hour
        dt_mins = _df['start'].dt.minute/60
        _df['linpos'] = dt_dow*24 + dt_hour + dt_mins
        _df['linpos'] = (_df['linpos'].round(1) * 10)
        _df['delta'] = ((_df['end'] - _df['start']).dt.total_seconds()) / 60
        return _df[['linpos', 'delta', 'station']].drop_duplicates()
    return (dt_to_linear,)


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
    return (cat10_dic,)


@app.cell
def _(mo, pl):
    df_ghost = pl.read_csv(
        str(mo.notebook_location() / 'public/ghosts.csv')
    )
    # Convert a column to datetime
    df_ghost = df_ghost.with_columns(
        pl.col('start').str.strptime(pl.Datetime).alias('start'),
        pl.col('end').str.strptime(pl.Datetime).alias('end')
    )
    df_fill = pl.read_csv(
        str(mo.notebook_location() / 'public/filling.csv')
    )
    df_fill = df_fill.with_columns(
        pl.col('start').str.strptime(pl.Datetime).alias('start'),
        pl.col('end').str.strptime(pl.Datetime).alias('end')
    )
    return df_fill, df_ghost


@app.cell
def _(Line, Polygon, Text, np):
    # Parameters for the spiral
    center_x = 400 # middle point of figure, in x
    center_y = 250 # middle point of figure, in y
    num_points = 1681 # 24 hours * 7 days
    angle_increment = np.pi / 800  # The angle increment for the spiral
    line_length_increment = 0.2  # The distance between each point (controls the spiral tightness)

    # Spiral line.
    spiral_elements = []
    line_pos = []
    angles = []
    radii = []
    x_prev = center_x
    y_prev = center_y
    starting_angle = np.pi
    for i in range(0, num_points):
        angle = starting_angle + i * angle_increment
        radius = i * line_length_increment
        x = center_x + radius * np.cos(angle)
        y = center_y + radius * np.sin(angle)
        line_pos.append((x, y))
        angles.append(angle)
        radii.append(radius)
        spiral_elements.append(
            Line(x1=x_prev, y1=y_prev, x2=x, y2=y, stroke="black", stroke_width=2)
        )
        x_prev, y_prev = x, y

    # Ticks for days
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday']
    dayposs = [0, 240, 480, 720, 960, 1200, 1440, 1680]
    day_elements = []
    day_text_elements = []
    _daylen = 15
    for ix, _d in enumerate(days):
        i = dayposs[ix]
        x, y = line_pos[i]

        # Calculate local env
        if i < len(line_pos) - 1:
            x_next, y_next = line_pos[i + 1]
        else:
            x_next, y_next = line_pos[i - 1]

        dx = x_next - x
        dy = y_next - y
        length = np.hypot(dx, dy)
        ndx = -dy / length
        ndy = dx / length

        x1 = x + _daylen * ndx
        y1 = y + _daylen * ndy
        x2 = x - _daylen * ndx
        y2 = y - _daylen * ndy

        day_elements.append(
            Line(x1=x1, y1=y1, x2=x2, y2=y2, stroke="black", stroke_width=3, class_='day')
        )
        # Add the text for the day name
        text_x = x + _daylen * ndx +5
        text_y = y + _daylen * ndy +5
        day_text_elements.append(
            Text(x=text_x, y=text_y, text=_d[0], font_size=12, fill="black", class_="day-label")
        )

    # # Add sinusoidal wave for day and night
    # Sinusoid parameters
    sinusoid_elements = []
    sinusoid_points = []  # Define this to store previous points for line connections
    amplitude = 10  # Height of sine wave
    frequency = 2 * np.pi / 240 # Full wave every 48 steps (~2 days)

    for i in range(0, num_points-1):
        # Base point on spiral
        x, y = line_pos[i]

        # Tangent vector (approximate using neighbors)
        if i == 1:
            x_prev, y_prev = line_pos[i]
            x_next, y_next = line_pos[i + 1]
        else:
            x_prev, y_prev = line_pos[i - 1]
            x_next, y_next = line_pos[i + 1]
        dx = x_next - x_prev
        dy = y_next - y_prev

        # Normalize and rotate to get normal vector
        length = np.hypot(dx, dy)
        ndx = -dy / length
        ndy = dx / length

        # Sinusoidal offset along the normal vector
        offset = 2 * amplitude * np.sin(i * frequency)

        # Final position offset from the spiral
        sx = x + offset * ndx
        sy = y + offset * ndy

        # Connect line segments
        if i > 1:
            px, py = sinusoid_points[-1]
            sinusoid_elements.append(
                Line(x1=px, y1=py, x2=sx, y2=sy, stroke="none", stroke_width=1.5, class_="sine")
            )

        # Store for next iteration
        sinusoid_points.append((sx, sy))


    # Define the start and end indices for the spiral segment
    start_i = 1
    end_i = len(sinusoid_points)
    # First path for the sinusoidal wave (day)
    sinusoidal_day_path = sinusoid_points

    # Second path for the spiral portion (night)
    spiral_segment = line_pos[start_i:start_i + end_i]
    spiral_segment_reversed = spiral_segment[::-1]

    # Define two different filled paths
    filled_path_day = sinusoidal_day_path + spiral_segment_reversed  # for 'day'
    filled_path_night = sinusoid_points + spiral_segment  # for 'night'

    # Create the 'day' polygon (light yellow fill)
    fill_element_day = Polygon(
        points=filled_path_day,
        fill="lightblue",
        stroke="none",
        opacity=0.3,
        class_="day-night-fill"
    )

    # Insert the day and night polygons into your sinusoid elements
    sinusoid_elements.insert(0, fill_element_day)
    #sinusoid_elements.insert(0, fill_element_night)
    return (
        amplitude,
        angle,
        angle_increment,
        angles,
        center_x,
        center_y,
        day_elements,
        day_text_elements,
        dayposs,
        days,
        dx,
        dy,
        end_i,
        fill_element_day,
        filled_path_day,
        filled_path_night,
        frequency,
        i,
        ix,
        length,
        line_length_increment,
        line_pos,
        ndx,
        ndy,
        num_points,
        offset,
        px,
        py,
        radii,
        radius,
        sinusoid_elements,
        sinusoid_points,
        sinusoidal_day_path,
        spiral_elements,
        spiral_segment,
        spiral_segment_reversed,
        start_i,
        starting_angle,
        sx,
        sy,
        text_x,
        text_y,
        x,
        x1,
        x2,
        x_next,
        x_prev,
        y,
        y1,
        y2,
        y_next,
        y_prev,
    )


@app.cell
def _(
    Circle,
    G,
    Text,
    cat10_dic,
    df_fill,
    df_ghost,
    dt_to_linear,
    line_pos,
    my_dropdown,
    np,
    pen_dist,
    radius_inflation_factor,
):
    # Events
    if my_dropdown.value == 'Ghosts !':
        _df = df_ghost
    else:
        _df = df_fill

    circle_elements = []
    _posdf = dt_to_linear(_df)
    _posdf

    for _ix, r in _posdf.iterrows():
        _i = r['linpos'].astype(int)

        _x, _y = line_pos[_i]

        # Calculate local env
        if _i < len(line_pos) - 1:
            _x_next, _y_next = line_pos[_i + 1]
        else:
            _x_next, _y_next = line_pos[_i - 1]

        _dx = _x_next - _x
        _dy = _y_next - _y
        _length = np.hypot(_dx, _dy)
        _ndx = -_dy / _length
        _ndy = _dx / _length

        cx = _x + (r['station']-6) * pen_dist.value * _ndx
        cy = _y + (r['station']-6) * pen_dist.value * _ndy

        _fillc = cat10_dic[r['station']]

        # Filling events are so short, that we need a conditional radius
        if my_dropdown.value == 'Ghosts !':
            _radius = radius_inflation_factor.value * r['delta']/5
        else:
            _radius = radius_inflation_factor.value * r['delta'] * 3

        circle_elements.append(G(elements=[
            Circle(
                cx=cx,
                cy=cy,
                r=_radius,
                fill=_fillc,
                fill_opacity=0.3,
                class_="my-circle",
                stroke="none",
                stroke_width=1
            ),
            Text(
                x=cx,
                y=cy,
                text=f"pen {r['station'].astype(int)}, event duration = {r['delta'].round(1)} (min)",  
                class_="tooltip-text",
            )
            ]))
    return circle_elements, cx, cy, r


@app.cell
def _(mo):
    my_dropdown = mo.ui.dropdown(
        options=["Ghosts !", "Refills !"],
        label="Ghost pigs or refilling events ?",
        allow_select_none = False,
        value='Ghosts !'
    )
    pen_dist = mo.ui.slider(start=1, stop=20, label="Distance between the pens ", value=3)
    radius_inflation_factor = mo.ui.slider(start=1, stop=10, label="Radius inflation factor", value=1)
    return my_dropdown, pen_dist, radius_inflation_factor


@app.cell
def _(my_dropdown):
    my_dropdown
    return


@app.cell
def _(pen_dist):
    pen_dist
    return


@app.cell
def _(radius_inflation_factor):
    radius_inflation_factor
    return


@app.cell
def _(
    SVG,
    circle_elements,
    day_elements,
    day_text_elements,
    mo,
    sinusoid_elements,
    spiral_elements,
):
    # Define the SVG plot
    plot = SVG(
        width=800,
        height=600,
        elements=spiral_elements + sinusoid_elements + circle_elements + day_elements + day_text_elements
    )
    mo.Html(plot.as_str())
    return (plot,)


if __name__ == "__main__":
    app.run()
