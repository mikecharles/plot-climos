#!/usr/bin/env python

# Built-in
import sys
import os
import warnings
from datetime import date

# Third-party
import jinja2
import pandas as pd
import numpy as np
from cpc.geogrids import Geogrid
from cpc.geoplot import Field, Map
from PIL import Image


warnings.filterwarnings("ignore", category=RuntimeWarning)

# --------------------------------------------------------------------------------------------------
# Define script usage
#
usage = """Usage: {} <CLIMO-TMPL>
  where:
    CLIMO-TMPL  template of climatology files - any $VAR strings (eg. $HOME) will be
                replaced with the corresponding environment variable, and {{mmdd}}
                will be replaced with the value of mmdd in a loop over days of the
                year in this script
    OUT-DIR     directory to write output image files to
""".format(os.path.basename(__file__))

# --------------------------------------------------------------------------------------------------
# Get command-line args
#
if len(sys.argv)-1 < 2:
    print(usage)
    exit(1)
else:
    climo_tmpl_str = sys.argv[1]
    out_dir = sys.argv[2]

# --------------------------------------------------------------------------------------------------
# Make a Jinja2 template from the climo file template
#
climo_templ = jinja2.Template(os.path.expanduser(os.path.expandvars(climo_tmpl_str)))

# --------------------------------------------------------------------------------------------------
# Create a Geogrid for plotting data
#
geogrid = Geogrid('1deg-global')

# --------------------------------------------------------------------------------------------------
# Loop over mmdd's (including 2/29) and create a plot for each day
#
for mmdd in pd.date_range('20000101', '20001231').strftime('%m%d'):
    # Render Jinja2 climo file template
    climo_file = climo_templ.render({'mmdd': mmdd})
    # Read in climo data
    data = np.fromfile(climo_file, 'float32')
    # Remove missing values
    data = np.where(data == -999, np.nan, data)

    # Create a Map
    title_date = date(2000, int(mmdd[0:2]), int(mmdd[2:4])).strftime('%d %b')
    title = 'Percent of Years Without Precip - {}'.format(title_date)
    map = Map(cbar_ends='square', title=title)
    # Create a Field
    field = Field(data, geogrid, levels=[0, 33.333, 66.666, 100],
                  fill_colors=['white', (1, 0.6, 0.16), (0.6, 0.2, .015)], fill_coastal_vals=True)
    # Plot Field
    map.plot(field)
    # Save plot
    os.makedirs(out_dir)
    plot_file = '{}/percent-dry-climo-{}.png'.format(out_dir, mmdd)
    map.save(plot_file, dpi=300)
    # Reduce file size
    im = Image.open(plot_file)
    im.convert('P', palette=Image.ADAPTIVE, colors=256).save(plot_file)



