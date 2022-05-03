#!/usr/bin/env python


"""
Copyright (C) by Almog Blaer 


╋╋╋╋╋╋╋╋╋╋╋┏━━━┓╋╋╋╋┏┓
╋╋╋╋╋╋╋╋╋╋╋┃┏━┓┃╋╋╋╋┃┃
┏━━┳━┳━━┳━━┫┃╋┗╋━━┳━┛┣━━┓
┃┏┓┃┏┫┃━┫┏┓┃┃╋┏┫┏┓┃┏┓┃┃━┫
┃┗┛┃┃┃┃━┫┗┛┃┗━┛┃┗┛┃┗┛┃┃━┫
┃┏━┻┛┗━━┫┏━┻━━━┻━━┻━━┻━━┛
┃┃╋╋╋╋╋╋┃┃
┗┛╋╋╋╋╋╋┗┛


prepCode (preparation Code) is aimed to mimic real seismic data traces.
The code input are synthetic raw velocity seismogram (raw data) in SAC foramt.
prepCode output converts the raw data to Mini-SEED (MSEED) format, own
stream of integers seismic data, contains all the traces, ready to be replay in 
the Israeli Earthquake Early Warning (EEW) algorithm - EPIC.
prepCode uses EPIC minimum velocity amplitude check (Pv), for determine the estimated P
arrival for the station. Pv value is 1e-5.5 cm/sec or 3.16e-8 m/sec**2

The main code steps are:
1. reading raw data traces, with 67.31 Hz sample rate 
2. the raw data is converted to acceleration (m/sec**2) and resampled to 40 Hz
3. first white noise adding, 110dB (relative to acceleration) and 120 sec long
4. second white noise adding, before P arrival
5. the re-processed seismogram's are multilayered by a gain factor (1e7 default)
6. the final prepCode value product is seismic acceleration data traces, with stram of
   integers units (counts).
"""

import numpy as np
import obspy
from obspy import read
from obspy import *
import pandas as pd
from obspy.geodetics import gps2dist_azimuth
import glob
import pylab as plt
from obspy import Trace
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
import matplotlib.pylab as plt
plt.rcParams.update({'font.size': 6})

class Calculator:
    """
    Calculating the distance and azimuth from the
    epicenter, for each station. The class methods
    implementing the values in the traces (3 channels X stations)
    """
    # global variables from the
      # stations file (lat lon station)
    _lines = []  # list of [lat lon station] lines

    def __init__(self, mag: float, depth: float, lat: float, lon: float):

        self.mag = mag  # The event magnitude
        self.depth = depth  # Te event depth
        self.lat = lat  # The event lon
        self.lon = lon  # The event lat
        self.path = 'traces/stations.d'
        # read the lines and write the mto global list _lines
        try:
            with open(self.path) as file_object:
                for line in file_object:
                    self._lines.append(line.rstrip())
                self._lines = [x.split(" ") for x in self._lines]

        except IOError:
            raise IOError("{} not found".format(
                self.path))

    def __repr__(self):
        """
        represents the Calculator class's objects
        as string, after the user settings:
        mag, depth, lat and lon
        :return: string as representation of object
        """
        return "< Synthetic earthquake: mag={};" \
               " depth={} km; lat={} deg; lon={} deg >".format(
            self.mag,
            self.depth,
            self.lat,
            self.lon)

    def get_data(self):
        """
        :return: getting the lines from stations file
        """
        return self._lines

    def calc(self, lat, lon):
        """
        Computes the distance between two geographic
        points on the WGS84 ellipsoid and the forward
        and backward azimuths between these points.
        (see obspy API Overview: https://docs.obspy.org/packages/autogen/obspy.geodetics.base.gps2dist_azimuth.html)
        :param lat: latitude of the epicenter
        :param lon: longitude of the epicenter
        :return:  a tuple of distance and back-azimuth for
                  the epicenter
        """
        return gps2dist_azimuth(lat,
                                lon,
                                self.lat,
                                self.lon, a=6378137.0, f=0.0033528106647474805)

    def time(self):
        """
        :return: evenly spaced time numbers over specified interval -t
        """
        tr = glob.glob('traces/*.z')[0]  # read one random trace
        tr = read(tr)
        t = np.linspace(0,
                        tr[0].stats.npts * tr[0].stats.delta,
                        tr[0].stats.npts)
        return t

    def pos(self, trace, _amp):
        """
        pos function gets one trace at a time from the
        stream generator, and calculates the P arrival
        position from it
        :param trace: an object containing seismic data
        :param _amp: amplitude check - min Pv, see reference:
        Chung, A. I., I. Henson, and R. M. Allen, 2019,
        Optimizing Earthquake Early Warning
        Performance: ElarmS-3, Seismological Research Letters,
         90, no. 2A, 727–743, doi:
        10.1785/0220180192.
        :return: P arrival time for the trace
        """
        t = self.time()
        position = np.argmax(abs(trace.data) > _amp)  # assuming the first sample of P arrival
        return t[position]  # translates the position to time

    def imp(self, trace):
        """
        :param trace: an object containing seismic data
        :return: trace valuable features: station name,
        lat, lon, epicentre distance and P arrival
        """
        P_arrivals = self.pos(trace, _amp=Picker.run.__defaults__[0])
        station = trace.stats.station
        for ln in self._lines:
            try:
                if ln[2] == station:
                    dist, azi, _ = self.calc(float(ln[0]),
                                             float(ln[1]))  # each station
                    return station, ln[0], ln[1], dist, azi, P_arrivals
                else:
                    continue
            except TypeError:
                return -1


class Picker(Calculator):
    """
    manual picking P arrivals, based on Pv amplitude check
    from Event Associator module (EA)
    :return: nice subplots' sheet of the all traces that were
             given, with manual P picking on
    :return: a dictionary with essential values
             (lat, lon, dist [km], azi [deg], P_trigger)
             for all given stations
    """

    def __init__(self, mag: float, depth: float, lat: float, lon: float):
        super().__init__(mag, depth, lat, lon)
        self.dict_dist_azi = dict()

    def read_z(cls):
        """
        class Picker method for reading all the traces as stream
        :return: stream generator
        """
        try:
            stream = read('traces/*.z')
            return iter(stream)
        except IOError:
            raise IOError("No traces are found in this directory")

    def change(self, trace):
        """
        rewrite dist and azi to the trace's header
        from the dictionary
        """

        station, channel = trace.stats.station, trace.stats.channel
        trace.stats.sac.dist, trace.stats.sac.az = (self.dict_dist_azi[station][2],
                                                    self.dict_dist_azi[station][3])
        trace.write(f'traces/{station}.{channel.lower()}', format='SAC')
        self.pos(trace, _amp=self.run.__defaults__[0])

    def figure(self, hspace, wspace, size):
        """
        create a figure and set of subplots
        :return figure with array of axes
        """
        fig, axs = plt.subplots(len(self.dict_dist_azi) // 2, 2, figsize=size, sharey=True)
        fig.subplots_adjust(hspace=hspace, wspace=wspace)
        axs = axs.ravel()
        return fig, axs

    def lines(self, trace, i, axs, ylim):
        """
        function to plot trace data against time
        """
        _amp = self.run.__defaults__[0]
        t = self.time()
        station, _, _, _, _, P_arrivals = self.imp(trace)
        axs[i].semilogy(t, np.abs(trace.data), label=str(trace.stats.channel))
        axs[i].axhline(_amp, c='g', ls='--', label='P waves - EPIC threshold')
        manual = abs(trace.data[int(P_arrivals / trace.stats.delta)])
        axs[i].scatter(P_arrivals, manual, color="r", label='manual P trigger')
        axs[i].set_title(station + " | " + "epicentre Distance ,m: " +
                         str(trace.stats.sac.dist) +
                         " | " + "P arrival ,sec: " +
                         str(format(P_arrivals, '.2f')))

        axs[i].set_ylim(ylim)
        axs[i].set_xlim(0, 40)
        axs[i].legend()
        axs[i].grid(True)
        axs[i].xaxis.set_major_locator(MultipleLocator(1))
        axs[i].xaxis.set_minor_locator(MultipleLocator(0.1))
        axs[i].set_xlabel('$time$, $sec$')
        axs[i].set_ylabel(r'$abs(log(Vel))$ ,$m/sec$')

    def picture_arrivals(self, size=(20, 100), ylim=(1e-9, 1e-2), hspace=1, wspace=.1, to_save=True):
        """
        gets the next raw trace from the iterator.
        shows the P arrival point on absolute log trace,
        based on the default minimum amplitude check - Pv
        :return dispy the figure, save it if to_sace=True
        """

        stream = self.read_z()
        fig, axs = self.figure(hspace, wspace, size)
        i = 0
        while True:
            try:
                rec = next(stream)
                self.lines(rec, i, axs, ylim)
                i += 1
            except StopIteration:
                if to_save:
                    plt.savefig('P_arrival.pdf',
                                bbox_inches='tight',
                                format='pdf')
                    plt.show()
                else:
                    plt.show()
                    return fig

    def read_all(self):
        """
        reading traces as stream
        :return: stream generator
        """
        try:
            stream = read('traces/*.[x, y, z]')
            return iter(stream)
        except IOError:
            raise IOError("No traces are found in this directory")

    def features(self, trace):
        """
        modify the header information,
        from the simulation coordinates
        (X-north, Y-east, Z-down) to ISN
        seismic network channels (BHN-north,
        BHE-east, BHZ=down)
        :param trace: an object containing seismic data
        :return: station name and channel
        """
        station = trace.stats.station
        trace.stats.network = 'IS'
        if trace.stats.channel == 'X':
            trace.stats.channel = 'BNN'
        elif trace.stats.channel == 'Y':
            trace.stats.channel = 'BNE'
        else:
            trace.stats.channel = 'BNZ'
        return station, trace.stats.channel

    def to_acc(self, trace, _sample_rate):
        """
        convert velocity trace data to
        acceleration (m/sec -> m/sec **2)
        :param trace: an object containing seismic data
        :param _sample_rate:
        :return: resampled data trace to
                 based on integer number
        """
        trace.resample(_sample_rate)
        trace.data = np.gradient(trace.data, trace.stats.delta)
        return trace

    def noise_before_trigger(self, trace, _noise_min, _noise_max):
        """
        first white noise adding, before P arrival.
        Samples are uniformly distributed over the
        half-open interval.
        :param trace: an object containing seismic data
        :param _noise_max: upper boundary of the output interval, relative to acc
        :param _noise_min: lower boundary of the output interval, relative to acc
        :return: uniformly distributed white noise with (P arrival / delta) samples
        """

        station, channel = self.features(trace)
        P_arrival = self.dict_dist_azi.get(station)[4]
        sample = int(P_arrival / trace.stats.delta)
        trace.data[:sample] = np.random.uniform(_noise_min, _noise_max, sample)

    def two_sec_noise(self, trace, _noise_min, _noise_max, _sample_rate, _sec):
        """
        second white noise adding, before 0 sec
        (simulation beginning)
        :param _sample_rate: see def noise_before_trigger
        :param _noise_max: see def noise_before_trigger
        :param _noise_min: see def noise_before_trigger
        :param trace: see def noise_before_trigger
        :param _sec: default 120 sec white noise
        :return:
        """

        noise = np.random.uniform(_noise_min,
                                  _noise_max,
                                  _sample_rate * _sec)
        trace.data = np.hstack((noise, trace.data))

    def gain(self, trace, _gain):
        """
        convert the data trace to stream of Integers,
        using gain factor.
        :param trace:
        :param _gain: default 1e7
        :return: data trace
        """

        trace.data = trace.data * _gain

    def picture(self, station_name,
                ax_xlim=(5, 28),
                ax_ylim=(-0.03, 0.03),
                yticks=0.005,
                xticks=1,
                size=(10, 15)):
        """
        depict the perpetrationCode steps
        for one station, ax - raw data,
        ax1 - vel gradient(acc), ax2 - 120 of
        white noise, ax3 - stream of integers
        :param station_name: station name
        :param ax_xlim: a. and b. subplots x limits
        :param ax_ylim: a. and b. subplots x limits
        :param yticks: tick locations and labels of the y-axis
        :param xticks: tick locations and labels of the x-axis
        :param size: figure size
        :return :4 subplots
        """

        fig, (ax, ax1, ax2, ax3) = plt.subplots(4, 1, figsize=size)
        fig.subplots_adjust(hspace=0.4, wspace=0.1)
        t = self.time()
        trace = read(f'traces/{station_name}.z')  # read raw trace - vel (m/sec)
        ax.scatter(t, trace[0].data, color="b", s=0.1, label='Raw data')
        ax.set_ylabel(r'$Vel ,m/sec$')
        ax.set_xlim(ax_xlim)
        ax.set_ylim(ax_ylim)
        ax.legend()
        ax.grid(True)
        ax.yaxis.set_major_locator(MultipleLocator(yticks))
        ax.xaxis.set_major_locator(MultipleLocator(1))
        ax.set_title(f'a)                               $Step$  $I$    |      No. samples: {trace[0].stats.npts}   |  '
                     f'sampling rate:  {str(round(trace[0].stats.sampling_rate, 2))} $Hz$')

        _sample_rate = self.run.__defaults__[5]  # import sample rate value, default 40 Hz
        # convert velocity trace data to acceleration (m/sec -> m/sec **2)
        trace = self.to_acc(trace[0], _sample_rate)
        t = np.linspace(0, trace.stats.npts * trace.stats.delta, trace.stats.npts)
        ax1.scatter(t, trace.data, color="r", s=0.1, label=f'BHZ')
        ax1.set_ylabel(r'$Acc ,m/sec^2$')
        ax1.set_xlim(ax_xlim)
        ax1.set_ylim(ax_ylim)
        ax1.legend()
        ax1.grid(True)
        ax1.yaxis.set_major_locator(MultipleLocator(yticks))
        ax1.xaxis.set_major_locator(MultipleLocator(xticks))
        ax1.set_title(f'b)                               $Step$  $II$    |      No. samples: {trace.stats.npts}   |  '
                      f'sampling rate:  {str(round(trace.stats.sampling_rate, 2))} $Hz$')

        _noise_max, _noise_min, _sample_rate = (self.run.__defaults__[1],
                                                self.run.__defaults__[2],
                                                self.run.__defaults__[5])
        t = np.linspace(0, self.run.__defaults__[4],
                        _sample_rate * self.run.__defaults__[4])
        # adding 120 sec of white noise
        noise = np.random.uniform(_noise_min,
                                  _noise_max,
                                  _sample_rate * self.run.__defaults__[4])
        dB = 20 * np.log10(abs(noise))
        ax2.plot(t, dB, 'r')
        ax2.grid(True)
        ax2.set_title(f'c)                               $Step$  $III$   |      120 sec white noise', loc='left')
        ax2.set_ylabel(r'$dB$ $relative$ $to$ $Acc$ ,$m/sec^2]^2$')
        ax2.xaxis.set_major_locator(MultipleLocator(10))
        ax2.yaxis.set_major_locator(MultipleLocator(10))
        ax2.set_xlim(0, self.run.__defaults__[4])

        # picking one og the prep trace data for the same demanded station
        trace = read(f'new_traces/{station_name}.new_bnz')
        t = np.linspace(0, trace[0].stats.npts * trace[0].stats.delta, trace[0].stats.npts)
        ax3.plot(t, trace[0].data, "k", label='Prep data')
        ax3.set_ylabel(r'$Stream of$ $Integers$ - $Acc$ * $gain$')
        ax3.set_xlim(ax_xlim[0] + self.run.__defaults__[4],
                     ax_xlim[1] + self.run.__defaults__[4])

        ax3.legend()
        ax3.grid(True)
        ax3.set_title(f'd)                              $Step$ $V$      |      No. samples: {trace[0].stats.npts}   |  '
                      f'sampling rate:  {str(round(trace[0].stats.sampling_rate, 2))} $Hz$')
        ax3.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        ax3.yaxis.set_major_locator(MultipleLocator(round(max(trace[0].data)) / 10))
        ax3.set_xlabel('$Time ,sec$', labelpad=5)
        plt.show()

    def write_dict(self):
        """
        writes dictionary values: stations
        and keys: lat, lon , dist, azi, P arrival
        :return: dict_dist_azi
        """

        stream = self.read_z()  # implementing dist and azi in each trace
        while True:
            try:
                rec = next(stream)  # yield new trace from the generator
                if self.imp(rec) == -1:
                    print(f"There is missing trace for {ln[2]} station")
                    continue
                else:
                    station, lat, lon, dist, azi, P_arrivals = self.imp(rec)  # adding distance and azi to the trace
                    self.dict_dist_azi[station] = (round(float(lat), 2),
                                                   round(float(lon), 2),
                                                   round(dist / 1000, 2),
                                                   round(azi, 2),
                                                   round(P_arrivals, 2))
                    self.change(rec)
            except StopIteration:
                break
        return self.dict_dist_azi

    def run(self, _amp=3.16e-8,
            _noise_max=1e-6,
            _noise_min=-1e-6,
            _gain=1e7,
            _sec=120,
            _sample_rate=40):

        dict_dist_azi = self.write_dict()
        stream = self.read_all()
        while True:
            try:
                rec = next(stream)  # read all the channels to stream and generate it to generator
                station, channel = self.features(rec)  # first: change the channels and network symbols
                self.to_acc(rec, _sample_rate=_sample_rate)  # second: resample the traces and convert them to acc
                self.noise_before_trigger(rec, _noise_max=_noise_max, _noise_min=_noise_min)  # third: first adding
                # white noise before the P arrival time
                self.two_sec_noise(rec, _noise_min=_noise_min,
                                   _noise_max=_noise_max,
                                   _sample_rate=_sample_rate,
                                   _sec=_sec)  # forth: second 120 sec white noise adding to the trace beginning
                self.gain(rec, _gain=_gain)  # fifth: multiply by 1e7 gain
                rec.write(f'new_traces/{station}.new_{channel.lower()}', format='SAC')

            except StopIteration:
                break

    if '__name' == '__main__':
        Picker.run()
