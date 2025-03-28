import marimo

__generated_with = "0.11.24"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md(
        r"""
        # Deployment of the pigs feed dataset

        Some information wrt. the dataset & ideas.
        """
    )
    return


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import plotly.express as px
    import pandas as pd
    return mo, pd, plt, px


@app.cell
def _(pd):
    df = pd.read_csv('raw_data/exp1_feeding_data.csv.gz', compression='gzip')
    # Redundant information can be removed
    del df['date']
    del df['hour']
    df['duration']
    df['start'] = pd.to_datetime(df['start'])
    df['end'] = pd.to_datetime(df['end'])

    return (df,)


@app.cell
def _(df):
    df.head()
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
