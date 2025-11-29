import os

import yaml


def to_dict(tsv):
    d = {}
    for line in tsv:
        line = line.strip()
        key, value = line.split("\t", 1)
        d[key] = value
    return d

conversion = to_dict(open("pacenotes_en.tsv"))

for file in os.listdir("../pacenotes"):
    content = f"""
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="ie=edge">
        <title>{file.replace(".yml", "")}</title>
        <style>
        body {{
            font-family: Helvetica, sans-serif;
            font-size: 30pt;
        }}
        table, th, td {{
            border: 3px solid;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 15px;
        }}
        td:first-child {{
            background-color: black;
            color: white;
            border-color: black;
            text-align: center;
        }}
        </style>
      </head>
      <body>
    <table>
    <thead>
    <tr>
    <th>Dist.</th>
    <th>Notes</th>
    </tr>
    </thead>
    <tbody>
    """
    pacenote = yaml.safe_load(open(f"../pacenotes/{file}"))
    for note in pacenote:
        content += f"""<tr>
        <td>{"{:.2f}".format(note["distance"] / 1000)}</td>
        <td>{" ".join([conversion[x] for x in note["notes"] if x in conversion])}</td>
        </tr>"""

    content += """
    </tbody>
    </table>
    </body>
    </html>
    """

    open(f"{file.replace(".yml", ".html")}", "w", encoding="utf-8").write(content)