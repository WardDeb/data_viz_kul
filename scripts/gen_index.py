# This script is based on:
# https://github.com/marimo-team/marimo-gh-pages-template/blob/main/scripts/build.py

import glob
import os


def generate_index():
    deploydir = "deploydir"
    index_path = os.path.abspath(os.path.join(deploydir, "index.html"))

    try:
        with open(index_path, "w") as f:
            f.write(
                """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>marimo</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
  </head>
  <body class="font-sans max-w-2xl mx-auto p-8 leading-relaxed">
    <div class="mb-8">
      <img src="https://raw.githubusercontent.com/marimo-team/marimo/main/docs/_static/marimo-logotype-thick.svg" alt="marimo" class="h-20" />
    </div>
    <div class="grid gap-4">
"""
            )
            for notebook in glob.glob(deploydir + '/*.html'):
                notebook_name = notebook.split("/")[-1].replace(".html", "")
                if notebook_name.lower() != 'index':
                  display_name = notebook_name.replace("_", " ").title()

                  f.write(
                      f'      <div class="p-4 border border-gray-200 rounded">\n'
                      f'        <h3 class="text-lg font-semibold mb-2">{display_name}</h3>\n'
                      f'        <div class="flex gap-2">\n'
                      f'          <a href="{notebook.split('/')[-1]}" class="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded">Open Notebook</a>\n'
                      f"        </div>\n"
                      f"      </div>\n"
                  )
            f.write(
                """    </div>
  </body>
</html>"""
            )
    except IOError as e:
        print(f"Error generating index.html: {e}")

generate_index()