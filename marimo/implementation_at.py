import marimo

__generated_with = "0.11.26"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _():
    import micropip
    return (micropip,)


@app.cell
async def _(micropip):
    await micropip.install(["svg-py", "pyarrow"])
    return


@app.cell
def _():
    import pandas as pd
    import numpy as np
    import polars as pl
    import datetime
    from math import pi
    from svg import SVG, Circle, G, Text, Polyline,Title, Path, Ellipse
    from datetime import datetime, timedelta,time
    from numpy import abs
    return (
        Circle,
        Ellipse,
        G,
        Path,
        Polyline,
        SVG,
        Text,
        Title,
        abs,
        datetime,
        np,
        pd,
        pi,
        pl,
        time,
        timedelta,
    )


@app.cell
def _():
    #ToDo:
    # testen ob weniger als 10000 punkte für die arcs möglich sind nach dem skalieren
    return


@app.cell(hide_code=True)
def _(abs, mo, pl):
    data2 = pl.read_csv(str(mo.notebook_location() / 'public/feeding_data.csv'),    null_values="NA")
    data = data2.to_pandas()
    #data = pd.read_csv('data_viz_kul/marimo/public/feeding_data.csv')
    data.rename(columns={' "tattoo"':'tattoo'}, inplace=True)
    data['intake'] = abs(data['intake'])
    data['rate'] = abs(data['rate'])
    return data, data2


@app.cell(hide_code=True)
def _(abs, data, pd):
    ########################################
    ########### DATA PREPROCESSING #########
    ########################################

    df_intake = data[['intake','start','end','tattoo','duration','hour','rate']]
    df_intake.loc[:, 'start'] = pd.to_datetime(df_intake['start'])
    df_intake.loc[:, 'end'] = pd.to_datetime(df_intake['end'])
    df_intake.loc[:, 'intake'] = abs(df_intake['intake'])
    return (df_intake,)


@app.cell(hide_code=True)
def _(datetime, df_intake, np, pd, time, timedelta):
    ########################################
    ########### CALCULATING ################
    ########################################

    def cumulative_intake(start_date,end_date, group_by_hour):
        a = datetime(start_date.year, start_date.month, start_date.day)
        start_date = pd.Timestamp(start_date) # convert to enable filtering
        end_date = pd.Timestamp(end_date) # convert to enable filtering
        df = df_intake[(df_intake['start']>=start_date)&(df_intake['end']<=end_date)] # filtering for rows between start and end
        df_cumu = df.set_index('start')
        hourly_sum = df_cumu['intake'].resample('h').sum().reset_index() # here we are summarizing the data by every hour by summing other the intake
        three_hourly_sum = hourly_sum.groupby(np.arange(len(hourly_sum)) // group_by_hour)['intake'].sum() # we summarize again in every 3 hours
        new_start_column = [a+timedelta(hours=i*group_by_hour) for i in range(len(three_hourly_sum))]
        for i in range(len(three_hourly_sum)):
            if new_start_column[i].time() < time(6, 0, 0) or new_start_column[i].time() >= time(18, 0, 0):
                three_hourly_sum[i] = -three_hourly_sum[i]
        df_new = pd.DataFrame({'start':new_start_column})
        three_hourly_sum = pd.concat([three_hourly_sum, df_new], axis=1)
        return three_hourly_sum

    def cartesian_to_polar(values, cx, cy):        
        gap_angle = 2*np.pi * 0.1
        angle_increment = ((2 * np.pi-gap_angle) / len(values))
        points = []
        baseline = 50 
        for i, v in enumerate(values):
            angle = i * angle_increment
            r = baseline + v  
            px = cx + r * np.cos(angle)  
            py = cy + r * np.sin(angle)  
            points.append(f"{px:.2f},{py:.2f}")
        return points

    def top_ten_pigs(date):
        date = pd.Timestamp(date)
        end_date = date+timedelta(hours=24)
        df = df_intake[(df_intake['start']>date)&(df_intake['end']<end_date)]
        df = df.groupby('tattoo')['intake'].sum().reset_index()
        df = pd.DataFrame(df).sort_values(by=['intake'], ascending=False)
        top_ten_pigs = df[df['tattoo']!='     FILLING']['tattoo'][:10]
        intakes = df[df['tattoo']!='     FILLING']['intake'][:10]
        return list(top_ten_pigs),list(intakes)

    def stats_top_ten(pigs,intakes, date):
        stats = []
        date = pd.Timestamp(date)
        end_date = date+timedelta(hours=24)
        df = df_intake[(df_intake['start']>date)&(df_intake['end']<end_date)]
        for i in range(10):
            pigs_df = df[(df['tattoo']==pigs[i])&(df['intake']!=0)]
            n_eating_times = len(pigs_df)
            avg_duration_per_sitting = pigs_df['duration'].sum()/n_eating_times
            avg_eating_rate = pigs_df['rate'].sum()/n_eating_times
            prefered_eating_hour = int(pigs_df.groupby('hour')['intake'].mean().reset_index().sort_values(by=['intake'], ascending=False).iloc[0]['hour'])
            stats.append({'pig':pigs[i],'total_intake':intakes[i], 'n_eat_times':n_eating_times, 'avg_duration':avg_duration_per_sitting, 'avg_eating_rate':avg_eating_rate, 'prefered_eat_hour':prefered_eating_hour, 'id':pigs[i]})
        return stats
    return cartesian_to_polar, cumulative_intake, stats_top_ten, top_ten_pigs


@app.cell(hide_code=True)
def _(Polyline, Text, Title, pd, timedelta):
    ########################################
    ########### CREATING SVG ###############
    ########################################

    def create_weightlabels(day_max, night_max, colors):
        day_labels = [f"{(day_max//3)*i} kg" for i in range(1,4)]
        night_labels = [f"{(night_max//3)*i} kg" for i in range(1,4)]
        labels = day_labels[::-1] + ["0 kg"] +night_labels
        lines = [Polyline(points = f"48,{i*32-5} 95,{i*32-5}", stroke=colors[i], fill='None', stroke_width=5) for i in range(len(colors)-1,-1,-1)]
        texts = [Text(text=f"{labels[i]}",font_size=15, x=100, y=(i)*32) for i in range(len(labels)-1,-1,-1)] 
        return texts+lines

    def create_hourlabels():
        lines = [Polyline(points = f"0,{i*50} -10,{i*50}", stroke='black', fill='None', stroke_width=5) for i in range(24)]
        texts = [Text(text=f"{i}:00", font_size=35, x=-90, y=i*50+10) for i in range(24)]
        return texts+lines

    def draw_polyline(points,color):
        polyline = Polyline(
            points=points,
            stroke=color,
            stroke_width=1,
            fill="None"
        )
        return polyline

    def draw_polyline2(points,color, group_by_hour, startdate):
        polylines = []
        n_points = int(24 / group_by_hour)
        for i in range(0,len(points), n_points):
            polylines.append(
                Polyline(
                    points=" ".join(points[i:i+n_points]),
                    stroke=color,
                    stroke_width=2,
                    fill='None',
                    class_="polyline",
                    id=f"{pd.Timestamp(startdate.value)+timedelta(hours=(i/n_points)*n_points)}",
                    elements=[Title(elements=[f'Information to {(pd.Timestamp(startdate.value)+timedelta(hours=(i/n_points)*n_points))}'])]
                )
            )

        return polylines
    return (
        create_hourlabels,
        create_weightlabels,
        draw_polyline,
        draw_polyline2,
    )


@app.cell
def _(Circle, Ellipse, G, Path, Title, np):
    class Pig:
        def __init__(self, eating_rate, duration, n_eating_times,prefered_eating_time,total_intake, id):
            self.e_rate = eating_rate
            self.n_times = n_eating_times
            self.duration = duration
            self.total_intake = total_intake
            self.pig_id = id
            self.cx = 0
            self.cy = 0
            self.eye_radius = np.log(1+duration)
            self.width = 4
            self.translate_y=prefered_eating_time
            self.stroke = 'black'
            self.fill = 'pink'

        def draw_head_ears(self):
            scale = self.e_rate
            whole_head = [
                    Path(
                        d="M 0,0 Q 25,15 50,0 Q 50,-25 25,-45 ", 
                        fill=self.fill,
                        stroke=self.stroke,
                        stroke_width=self.width,
                        transform="rotate(200), translate(23,40)"
                    ),
                    Path(
                        d="M 0,0 Q 25,15 50,0 Q 50,-25 25,-45 ", 
                        fill=self.fill,
                        stroke=self.stroke,
                        stroke_width=self.width,
                        transform="rotate(290), translate(23,40)"
                    ),
                    Circle(
                        cx = self.cx, 
                        cy = self.cy,
                        r=50, 
                        fill=self.fill, 
                        stroke=self.stroke,
                        stroke_width=self.width
                    ),
                ]
            return G(
                elements=whole_head,
                transform=f"scale({scale},{scale})"
            )

        def draw_eyes(self):
            eyes = [
                Circle(
                    cx=2*self.eye_radius, 
                    cy=-self.eye_radius,
                    r=self.eye_radius,
                    stroke=self.stroke, 
                    stroke_width=self.width
                ),
                Circle(
                    cx=-2*self.eye_radius, 
                    cy=-self.eye_radius,
                    r=self.eye_radius,
                    stroke=self.stroke, 
                    stroke_width=self.width
                ),   
            ]
            return G(
                elements=eyes,
                transform=f"translate(0,{-1.5*self.eye_radius})"
            )

        def draw_nose(self):
            nose_hole = max(self.n_times / 5, 1)
            nose = Ellipse(
                cx=0,
                cy=0,
                rx=self.n_times,
                ry=self.n_times//2,
                fill=self.fill,
                stroke=self.stroke,
                stroke_width=self.width
            )    
            nostrils = [
                Circle(
                    cx=-self.n_times * 0.3,
                    cy=0,
                    r=nose_hole,
                    fill="black"),
                Circle(
                    cx=self.n_times * 0.3,
                    cy=0,
                    r=nose_hole,
                    fill="black")
            ]
            return G(
                elements=[nose] + nostrils,
                transform = f"translate(0,{2*self.eye_radius})"
            )

        def draw_pig(self, position_x):
            return G(
                elements=[
                    Title(text=f"Pig: {self.pig_id}\n| Avg eating rate: {self.e_rate:.2f} kg/s \n| Avg duration per sitting: {self.duration:.2f}s \n| Total times eating: {self.n_times} \n| prefered eating time: {self.translate_y}:00 \n| total intake {self.total_intake:.2f} kg"),
                    self.draw_head_ears(),
                    self.draw_eyes(),
                    self.draw_nose()
                ],
                transform=f"translate({position_x},{self.translate_y*50})"
            )
    return (Pig,)


@app.cell
def _(
    cartesian_to_polar,
    cumulative_intake,
    draw_polyline,
    end_date,
    start_date,
):
    ########################################
    ########### PLOTTING ###################
    ########################################
    grouped_by_hour = 1
    df_cumu = cumulative_intake(start_date.value, end_date.value,grouped_by_hour)
    x = df_cumu['intake'].tolist()
    points = cartesian_to_polar(x,100,100)
    points2 = points.copy()

    values= [max(df_cumu['intake'])*i//3 for i in range(3,-1,-1)] + [min(df_cumu['intake'])*i//3 for i in range(1,4)]

    colors = ['#FF8561', '#FFB761', '#F9FF61', '#000000', '#A6F58F', '#9ABDE4', '#074285']

    arc_points = [cartesian_to_polar([i for _ in range(10000)], 100, 100) for i in values]

    arcs = [draw_polyline(points, color) for points,color in zip(arc_points, colors)]
    return (
        arc_points,
        arcs,
        colors,
        df_cumu,
        grouped_by_hour,
        points,
        points2,
        values,
        x,
    )


@app.cell
def _(mo):
    start_date = mo.ui.date(label="Start Date", start="2020-12-04",stop="2021-03-08")
    end_date = mo.ui.date(label="End Date", start="2020-12-05",stop="2021-03-08")
    return end_date, start_date


@app.cell
def _(end_date, mo, start_date):
    date_picker = mo.ui.date(label="Pick a Date to show pig eating behaviour", start=start_date.value, stop=end_date.value)
    return (date_picker,)


@app.cell
def _(
    G,
    SVG,
    Text,
    arcs,
    colors,
    create_weightlabels,
    df_cumu,
    draw_polyline2,
    end_date,
    grouped_by_hour,
    points,
    start_date,
):
    ### Elements ###
    header_svg1 = Text(text=f"Cumulative food intake per hour from {start_date.value} to {end_date.value}",x=10,y=25,font_size=30)

    axis = G(
        elements=arcs,
    )

    poly = G(
        elements=[draw_polyline2(points,'black',grouped_by_hour, start_date)],
    )

    texts = G(
            elements=create_weightlabels(max(df_cumu['intake']),min(df_cumu['intake']), colors),
            transform="translate(-10,100)"
        )

    elements = G(
            elements=[axis, poly],
            transform="rotate(-70,100,100) scale(3,3) translate(-90,100)"
        )

    plot1 = SVG(
        width=900,
        height=1000,
        elements=[header_svg1,elements,texts],
    )
    plot1_html = plot1.as_str()
    return axis, elements, header_svg1, plot1, plot1_html, poly, texts


@app.cell
def _(Pig, date_picker, stats_top_ten, top_ten_pigs):
    #date = datetime.strptime(tooltip.text.split(" ")[-1], "%Y-%m-%d").date()
    date = date_picker.value

    summary,intakes = top_ten_pigs(date)
    pig_stats = stats_top_ten(summary, intakes, date)
    stats = sorted(pig_stats, key=lambda pig: pig['avg_eating_rate'])
    pig_elements=[]
    position_x = [0]
    for i in range(10):
        pig_elements.append(Pig(stats[i]['avg_eating_rate'],
                           stats[i]['avg_duration'],
                           stats[i]['n_eat_times'],
                           stats[i]['prefered_eat_hour'],
                           stats[i]['total_intake'],
                           stats[i]['id'])
                          )
        position_x.append( position_x[len(position_x)-1] + 2*50*stats[i]['avg_eating_rate'])
    return (
        date,
        i,
        intakes,
        pig_elements,
        pig_stats,
        position_x,
        stats,
        summary,
    )


@app.cell
def _(
    G,
    Polyline,
    SVG,
    Text,
    create_hourlabels,
    date_picker,
    pig_elements,
    position_x,
    stats,
):
    pigs_svg = G(
        elements=[
            [pig.draw_pig(i) for pig,i in zip(pig_elements,position_x[1:])]
        ],
    )
    axes = Polyline(
        points=f"0,1200 0,0 {position_x[-1]+stats[9]['avg_eating_rate']*50},0",
        stroke_width=4,
        stroke='black',
        fill='None'
    )

    header_svg2 = Text(
            x=-100, 
            y=-130, 
            text=f"pig eating behaviour of {date_picker.value}", 
            font_size=100,
    )

    x_labels = Text(text="total intake ranked from least to most", x=0,y=-10, font_size=30)

    y_labels = G(
        elements=create_hourlabels(),
    )

    plot2_elements=G(
        elements = [header_svg2,axes,x_labels,y_labels,pigs_svg],
        transform='translate(0,200)'
    )

    plot2 = SVG(
        height=1000,
        width=1000,
        viewBox="0 0 2400 3000",
        elements=[plot2_elements]
    )
    plot2_html = plot2.as_str()
    return (
        axes,
        header_svg2,
        pigs_svg,
        plot2,
        plot2_elements,
        plot2_html,
        x_labels,
        y_labels,
    )


@app.cell
def _(date_picker, end_date, mo, start_date):
    mo.hstack([start_date, end_date,date_picker]).style({'width':'1000px'})
    return


@app.cell
def _(mo, plot1_html, plot2_html):
    mo.iframe(plot1_html+plot2_html,height=2000, width=2000)
    return


@app.cell
def _():
    #Questions: should I consider the FILLING and GHOSTPIGS visits or not? Well they do represent a significant portion of the consumption, but its unclear which pigs are the FILLINGS
    return


@app.cell
def _():
    #ToDo:
    return


if __name__ == "__main__":
    app.run()
