#! /usr/bin/env python
import os
import xarray as xr
import pandas as pd
import functions.plotting as pf
import functions.common as cf
import matplotlib.pyplot as plt
import re
import numpy as np

fmt = '%Y.%m.%dT%H.%M.00'


def mk_str(attrs, str_type='t'):
    """
    make a string of either 't' for title. 's' for file save name.
    """
    site = attrs['subsite']
    node = attrs['node']
    sensor = attrs['sensor']
    stream = attrs['stream']

    if str_type is 's':
        string = site + '-' + node + '-' + sensor + '-' + stream + '-'
    else:
        string = site + '-' + node + '\nStream: ' + stream + '\n' + 'Variable: '
    return string


def read_file(fname):
    file_list = []
    with open(fname) as f:
        for line in f:
            if line.find('#') is -1:
                file_list.append(line.rstrip('\n'))
            else:
                continue
    return file_list


def main(files, out, time_break='full'):
    """
    files: url to an .nc/.ncml file or the path to a text file containing .nc/.ncml links. A # at the front will skip links in the text file.
    out: Directory to save plots
    """
    fname, ext = os.path.splitext(files)
    if ext in '.nc':
        list_files = [files]
    elif ext in '.ncml':
        list_files = [files]
    else:
        list_files = read_file(files)

    stream_vars = pf.load_variable_dict(var='eng')  # load engineering variables
    for nc in list_files:
        print nc
        with xr.open_dataset(nc, mask_and_scale=False) as ds:
            # change dimensions from 'obs' to 'time'
            ds = ds.swap_dims({'obs': 'time'})
            ds_variables = ds.data_vars.keys()  # List of dataset variables
            title_pre = mk_str(ds.attrs, 't')  # , var, tt0, tt1, 't')
            platform = ds.subsite
            node = ds.node
            sensor = ds.sensor
            save_dir = os.path.join(out, ds.subsite, ds.node, ds.stream, 'timeseries')
            cf.create_dir(save_dir)

            misc = ['quality', 'string', 'timestamp', 'deployment', 'id', 'provenance', 'qc',  'time', 'mission', 'obs',
            'volt', 'ref', 'sig', 'amp', 'rph', 'calphase', 'phase', 'therm']

            # reg_ex = re.compile('|'.join(eng+misc))  # make regular expression
            reg_ex = re.compile('|'.join(misc))

            #  keep variables that are not in the regular expression
            sci_vars = [s for s in ds_variables if not reg_ex.search(s)]

            if not time_break is 'full':
                times = np.unique(ds[time_break])
            else:
                times = [0]
            
            for t in times:
                if not time_break is 'full':
                    time_ind = t == ds[time_break].data
                else:
                    time_ind = np.ones(ds['time'].data.shape, dtype=bool) # index all times to be set to True

                for var in sci_vars:
                    x = dict(data=ds['time'].data[time_ind],
                             info=dict(label='Time', units='GMT'))
                    t0 = pd.to_datetime(x['data'].min()).strftime('%Y-%m-%dT%H%M%00')
                    t1 = pd.to_datetime(x['data'].max()).strftime('%Y-%m-%dT%H%M%00')
                    try:
                        sci = ds[var]
                        print var
                    except UnicodeEncodeError: # some comments have latex characters
                        ds[var].attrs.pop('comment')  # remove from the attributes
                        sci = ds[var]  # or else the variable won't load

                    try:
                        y_lab = sci.long_name
                    except AttributeError:
                        y_lab = sci.standard_name
                    y = dict(data=sci.data[time_ind], info=dict(label=y_lab, units=sci.units, var=var,
                                                                platform=platform, node=node, sensor=sensor))

                    title = title_pre + var

                    # plot timeseries with outliers
                    fig, ax = pf.auto_plot(x, y, title, stdev=None, line_style='r-o', g_range=True)
                    pf.resize(width=12, height=8.5)  # Resize figure

                    save_name = '{}-{}-{}_{}_{}-{}'.format(platform, node, sensor, var, t0, t1)
                    pf.save_fig(save_dir, save_name, res=150)  # Save figure
                    plt.close('all')

                    # plot timeseries with outliers removed
                    fig, ax = pf.auto_plot(x, y, title, stdev=1, line_style='r-o', g_range=True)
                    pf.resize(width=12, height=8.5)  # Resize figure

                    save_name = '{}-{}-{}_{}_{}-{}_outliers_removed'.format(platform, node, sensor, var, t0, t1)
                    pf.save_fig(save_dir, save_name, res=150)  # Save figure
                    plt.close('all')
                del x, y

if __name__ == '__main__':
    times = 'time.month' # set times = 'full' to plot entire dataset
    file = 'http://opendap.oceanobservatories.org:8090/thredds/dodsC/ooi/friedrich-knuth-gmail/20161007T055559-RS01SBPS-PC01A-05-ADCPTD102-streamed-adcp_velocity_beam/deployment0000_RS01SBPS-PC01A-05-ADCPTD102-streamed-adcp_velocity_beam.ncml'
    main(file, '/Users/knuth/Desktop/adcp/timeseries', times)

