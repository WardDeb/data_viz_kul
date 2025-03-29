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
    await micropip.install("plotly")
    await micropip.install("pandas")
    import plotly
    return (plotly,)


@app.cell
def _():
    import pandas as pd
    import plotly.express as px
    return pd, px


@app.cell
def _(mo):
    mo.md(
        r"""
        # Pig feeding interactive example

        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
        """
    )
    return


@app.cell
def _(mo, pd):
    df = pd.read_csv(
        str(mo.notebook_location() / 'public/subset.csv')
    )
    # Redundant information can be removed
    del df['date']
    del df['hour']
    df['start'] = pd.to_datetime(df['start'])
    df['end'] = pd.to_datetime(df['end'])
    return (df,)


@app.cell
def _(df, mo, px):
    plot = mo.ui.plotly(
      px.scatter(x=df['rate'], y=df['intake'], width=600, height=300)
    )
    plot
    return (plot,)


if __name__ == "__main__":
    app.run()
