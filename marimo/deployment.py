import marimo

__generated_with = "0.11.31"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import plotly.express as px
    import pandas as pd
    import polars as pl
    import pyarrow
    return mo, pd, pl, plt, px, pyarrow


@app.cell
def _(mo):
    mo.md(r"""# Pig feeding interactive example""")
    return


@app.cell
def _(mo, pd, pl):
    df = pl.read_csv(
        str(mo.notebook_location() / 'processed_data/subset.csv')
    ).to_pandas()
    # Redundant information can be removed
    del df['date']
    del df['hour']
    df['start'] = pd.to_datetime(df['start'])
    df['end'] = pd.to_datetime(df['end'])
    return (df,)


@app.cell
def _(mo):
    mo.md(r"""# Example of an interactive plot""")
    return


@app.cell
def _(df, mo, px):
    plot = mo.ui.plotly(
      px.scatter(x=df['rate'], y=df['intake'], width=600, height=300)
    )
    plot
    return (plot,)


if __name__ == "__main__":
    app.run()
