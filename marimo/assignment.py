import marimo

__generated_with = "0.11.26"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import pandas as pd
    import numpy as np
    from math import pi
    from svg import SVG, Circle, G, Text, Polyline,Title, Path
    from datetime import datetime, timedelta,time
    from numpy import abs
    import random
    return (
        Circle,
        G,
        Path,
        Polyline,
        SVG,
        Text,
        Title,
        abs,
        datetime,
        mo,
        np,
        pd,
        pi,
        random,
        time,
        timedelta,
    )


@app.cell
def _():
    #ToDo:
    # testen ob weniger als 10000 punkte für die arcs möglich sind nach dem skalieren
    # correctly scale the ears
    return


@app.cell
def _(abs, pd):
    data = pd.read_csv('data_viz_kul/raw_data/Exp1 - Feeding data.csv')
    data.rename(columns={' "tattoo"':'tattoo'}, inplace=True)
    data['intake'] = abs(data['intake'])
    data['rate'] = abs(data['rate'])
    return (data,)


@app.cell
def _(abs, data, pd):
    ########################################
    ########### DATA PREPROCESSING #########
    ########################################

    df_intake = data[['intake','start','end','tattoo','duration','hour','rate']]
    df_intake.loc[:, 'start'] = pd.to_datetime(df_intake['start'])
    df_intake.loc[:, 'end'] = pd.to_datetime(df_intake['end'])
    df_intake.loc[:, 'intake'] = abs(df_intake['intake'])
    return (df_intake,)


@app.cell
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
            stats.append({'pig':pigs[i],'total_intake':intakes[i], 'n_eat_times':n_eating_times, 'avg_duration':avg_duration_per_sitting, 'avg_eating_rate':avg_eating_rate, 'prefered_eat_hour':prefered_eating_hour})
        return stats
    
    return cartesian_to_polar, cumulative_intake, stats_top_ten, top_ten_pigs


@app.cell(hide_code=True)
def _(mo):
    start_date = mo.ui.date(label="Start Date", start="2020-12-04",stop="2021-03-08")
    end_date = mo.ui.date(label="End Date", start="2020-12-05",stop="2021-03-08")
    return end_date, start_date


@app.cell
def _(end_date, mo, start_date):
    mo.hstack([start_date, end_date]).style({'width':'500px'})
    return


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
                    class_="abc",
                    elements=[Title(elements=[f'Information to {(pd.Timestamp(startdate.value)+timedelta(hours=(i/n_points)*n_points))}'])]
                )
            )

        return polylines
    return create_weightlabels, draw_polyline, draw_polyline2


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
    grouped_by_hour,
    points,
    start_date,
):
    ### Elements ###
    axis = G(
        elements=arcs,
    )

    poly = G(
        elements=[draw_polyline2(points,'black',grouped_by_hour, start_date)],
    )

    texts = G(
            elements=create_weightlabels(max(df_cumu['intake']),min(df_cumu['intake']), colors),
            transform="translate(0,100)"
        )

    tooltip = G(
        id="tooltip",
        elements=[
            Text(x=700, y=50, text="Click across the graph", id="tooltiptext")
        ],
    )

    elements = G(
            elements=[axis, poly],
            transform="rotate(-70,100,100) scale(3,3) translate(-90,50)"
        )

    plot = SVG(
        width=1000,
        height=1000,
        elements=[elements,texts, tooltip]
    )
    #mo.iframe(plot.as_str()+script)
    return axis, elements, plot, poly, texts, tooltip


@app.cell
def _():
    #Todo: Create second plot
    return


@app.cell
def _(Circle, G, Path, np):
    class Pig:
        def __init__(self, eating_rate, duration, n_eating_times,prefered_eating_time,total_intake):
            self.e_rate = eating_rate
            self.duration = duration
            self.n_times = n_eating_times
            self.cx = 0
            self.cy = 0
            self.eye_radius = np.log(1+self.duration)
            self.width = 4
            self.translate_x=prefered_eating_time
            self.translate_y=total_intake
            self.stroke = 'black'
            self.fill = 'pink'
        
        def draw_eyes(self,):
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
            return eyes

        def draw_head_ears(self):
            scale = 1+self.e_rate
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
    
        def draw_nose(self):
            nose_hole = max(self.n_times/5,1)
            nose = Path(
                d=f"M 0,0 a {2*self.n_times},{self.n_times} 0 1,0 1,0 z M -7,15 a {nose_hole},{nose_hole} 0 1,0 1,0 z M 7,15 a {nose_hole},{nose_hole} 0 1,0 1,0 z", 
                fill=self.fill,
                stroke=self.stroke,
                stroke_width=self.width
            )
            return nose

        def draw_pig(self):
            print(self.translate_x*100,self.translate_y*100)
            return G(
                elements=[
                    self.draw_head_ears(),
                    self.draw_eyes(),
                    self.draw_nose()
                ],
                transform="translate(1900,1820)",
                #transform=f"translate({self.translate_x*100},{self.translate_y*100})"
            )
        
    return (Pig,)


@app.cell
def _(Pig, start_date, stats_top_ten, top_ten_pigs):
    summary,intakes = top_ten_pigs(start_date.value)
    stats = stats_top_ten(summary, intakes, start_date.value)
    pig_elements=[]
    for i in range(10):
        pig_elements.append(Pig(stats[i]['avg_eating_rate'],
                           stats[i]['avg_duration'],
                           stats[i]['n_eat_times'],
                           stats[i]['prefered_eat_hour'],
                           stats[i]['total_intake'])
                          )
    return i, intakes, pig_elements, stats, summary


@app.cell
def _(G, Pig, Polyline, SVG, stats):
    pig1= Pig(stats[0]['avg_eating_rate'],stats[0]['avg_duration'],stats[0]['n_eat_times'],stats[0]['total_intake'], stats[0]['prefered_eat_hour'])

    elements3 = G(
        elements=[
            pig1.draw_pig()
        ],
    )
    axes = Polyline(
        points="0,1000 0,0 2000,0",
        stroke_width=6,
        stroke='black',
        fill='None'
    )

    plot2=SVG(
        height=3000,
        width=2400,
        elements = [axes,elements3]
    )
    #mo.iframe(plot2.as_str())
    return axes, elements3, pig1, plot2


@app.cell
def _():
    return


@app.cell
def _():
    #Questions: should I consider the FILLING and GHOSTPIGS visits or not? Well they do represent a significant portion of the consumption, but its unclear which pigs are the FILLINGS
    return


if __name__ == "__main__":
    app.run()
