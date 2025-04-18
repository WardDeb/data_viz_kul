import marimo

__generated_with = "0.11.31"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import seaborn as sns
    return mo, pl, sns


@app.cell
def _(mo):
    mo.md(
        r"""
        # Exploration

        Initial exploration of the data, read up the data and pre-process it. The main work we need to do is make sure the date, start & end are proper datetimes, and filter the data:

        First of all, instances with tattoo == 'filling' aren't feeding events, but rather filling of the trough. Additionaly, instances with pig == 0 and tattoo == 'filling' or 'ghost' are either fillings or erroneous measurements (no pig id registered). These should be filtered.
        """
    )
    return


@app.cell
def _(pl):
    # Read up data, parse to filling / ghost dataframes and save into the public folder for implementation.
    df = pl.read_csv(
        'raw_data/exp1_feeding_data.csv.gz'
    )
    df = df.with_columns(
        pl.col("date").str.to_datetime("%Y-%m-%d").alias("date"),
        pl.col("start").str.to_datetime("%Y-%m-%d %H:%M:%S").alias("start"),
        pl.col("end").str.to_datetime("%Y-%m-%d %H:%M:%S").alias("end"),
        pl.col("tattoo").str.strip_chars().alias("tattoo")
    )
    df_fill = df.filter(
        (pl.col("tattoo") == "FILLING" )
    )
    df_ghost = df.filter(
        (pl.col("tattoo") == "GHOST VISIT")
    )
    df_proper = df.filter(
        (pl.col("tattoo") != "GHOST VISIT"),
        (pl.col("tattoo") != "FILLING")
    )
    df_fill.to_pandas()[['start', 'end', 'station']].to_csv('marimo/public/filling.csv')
    df_ghost.to_pandas()[['start', 'end', 'station']].to_csv('marimo/public/ghosts.csv')
    df_proper.to_pandas()[['tattoo', 'start', 'end', 'intake', 'station']].to_csv('marimo/public/proper_events.csv')
    return df, df_fill, df_ghost, df_proper


@app.cell
def _(df):
    df["tattoo"].unique()
    return


@app.cell
def _(df):
    df["pig"].unique()
    return


if __name__ == "__main__":
    app.run()
