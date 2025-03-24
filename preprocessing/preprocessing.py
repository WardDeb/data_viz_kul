import marimo

__generated_with = "0.11.24"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import seaborn as sns

    import warnings
    warnings.filterwarnings("ignore", category=UserWarning)
    return mo, pd, sns, warnings


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
def _(pd):
    df = pd.read_csv('raw_data/exp1_feeding_data.csv.gz', compression='gzip')
    # Redundant information can be removed
    del df['date']
    del df['hour']
    df['duration']
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


if __name__ == "__main__":
    app.run()
