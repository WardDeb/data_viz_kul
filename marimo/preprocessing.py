import marimo

__generated_with = "0.11.31"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import polars as pl
    import seaborn as sns
    import pandas as pd

    import warnings
    warnings.filterwarnings("ignore", category=UserWarning)
    return mo, pd, pl, sns, warnings


@app.cell
def _(mo):
    mo.md(
        r"""
        # Exploration

        Initial exploration of the data, read up the data and make some plots.
        Make sure our date, start and end are parsed appropriately as time.
        """
    )
    return


@app.cell
def _(pd, pl):
    df = pl.read_csv(
        'raw_data/exp1_feeding_data.csv.gz'
    ).to_pandas()
    # Redundant information can be removed
    del df['date']
    del df['hour']
    df['start'] = pd.to_datetime(df['start'])
    df['end'] = pd.to_datetime(df['end'])
    print(df.dtypes)
    return (df,)


@app.cell
def _(df, sns):
    sns.violinplot(
        data=df,
        x='station',
        y='intake'
    )
    return


@app.cell
def _(df, sns):
    sns.violinplot(
        data=df,
        x='station',
        y='duration'
    )
    return


@app.cell
def _(df):
    df.groupby('pig')['station'].nunique()
    return


@app.cell
def _(df):
    df
    return


if __name__ == "__main__":
    app.run()
