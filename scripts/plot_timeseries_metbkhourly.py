#! /usr/bin/env python
"""
@file plot_timeseries_metbkhourly.py
@author Lori Garzio
@email lgarzio@marine.rutgers.edu
@brief This is a wrapper script that imports the tools: plotting and common as python methods.

@usage This script creates timeseries plots for metbk_hourly data streams. Two plots for each parameter are created: 
1) all data, and 2) outliers removed. data from multiple netCDF files located in one directory.

rootdir: Directory containing netCDF files to plot. Data from all files located in this directory will be 
plotted on the same figure.
sDir: Directory where plots will be saved.
"""

import os
import xarray as xr
import functions.plotting as pf
import functions.common as cf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re

rootdir = '/Users/lgarzio/Documents/OOI/GI01SUMO/GI01SUMO-SBD11-06-METBKA000/deployment0001'
sDir = '/Users/lgarzio/Documents/OOI/GI01SUMO/GI01SUMO-SBD11-06-METBKA000/plots'

# Identifies variables to skip when plotting
misc_vars = ['quality', 'string', 'timestamp', 'deployment', 'id', 'provenance', 'qc',  'time', 'mission', 'obs',
            'volt', 'ref', 'sig', 'amp', 'rph', 'calphase', 'phase', 'therm', 'error_code', 'analog', 'lat', 'lon',
             'serial_number', 'ct_depth',]

reg_ex = re.compile('|'.join(misc_vars))

list_files = rootdir + '/*.nc'

for root, dirs, files in os.walk(rootdir):
    for filename in files: # get info from one file
        if filename.endswith('.nc'):
            print filename
            file = os.path.join(root,filename)
            f = xr.open_dataset(file)
            fN = f.source
            platform = f.subsite
            node = f.node
            sensor = f.sensor
            title = platform + '-' + node + '-' + sensor

            global fName
            head, tail = os.path.split(filename)
            fName = tail.split('.', 1)[0]
            d = fName.split('_')[0]

            save_dir = os.path.join(sDir, 'timeseries', d)
            cf.create_dir(save_dir)

            varList = []
            for vars in f.variables:
                varList.append(str(vars))

            yVars = [s for s in varList if not reg_ex.search(s)]

            with xr.open_mfdataset(list_files) as ds:  # open all files and plot

                for v in yVars:
                    print v

                    t = ds['met_timeflx'].data
                    t_dict = dict(data = t, info = dict(label='Time', units='GMT'))

                    y = ds[v]

                    y_dict = dict(data = y.data, info = dict(label=v, units = y.units, var = v, platform = platform,
                                                             node = node, sensor = sensor))

                    # plot timeseries with outliers
                    fig, ax = pf.auto_plot(t_dict, y_dict, title, stdev=None, line_style='.', g_range=True, color=None)
                    pf.resize(width=12, height=8.5)  # Resize figure

                    # format date axis
                    df = mdates.DateFormatter('%Y-%m-%d')
                    ax.xaxis.set_major_formatter(df)
                    fig.autofmt_xdate()

                    save_file = os.path.join(save_dir, fName + '_' + v)
                    plt.savefig(str(save_file),dpi=150) # save figure
                    plt.close('all')

                    # plot timeseries with outliers removed
                    fig, ax = pf.auto_plot(t_dict, y_dict, title, stdev=3, line_style='.', g_range=True, color=None)
                    pf.resize(width=12, height=8.5)  # Resize figure

                    # format date axis
                    df = mdates.DateFormatter('%Y-%m-%d')
                    ax.xaxis.set_major_formatter(df)
                    fig.autofmt_xdate()

                    save_file = os.path.join(save_dir, fName + '_' + v + '_outliers_removed')
                    plt.savefig(str(save_file),dpi=150) # save figure
                    plt.close('all')