
*Copyright (c) 2022 by Almog Blaer*

```

                                    ╋╋╋╋╋╋╋╋╋╋╋┏━━━┓╋╋╋╋┏┓
                                    ╋╋╋╋╋╋╋╋╋╋╋┃┏━┓┃╋╋╋╋┃┃
                                    ┏━━┳━┳━━┳━━┫┃╋┗╋━━┳━┛┣━━┓
                                    ┃┏┓┃┏┫┃━┫┏┓┃┃╋┏┫┏┓┃┏┓┃┃━┫
                                    ┃┗┛┃┃┃┃━┫┗┛┃┗━┛┃┗┛┃┗┛┃┃━┫
                                    ┃┏━┻┛┗━━┫┏━┻━━━┻━━┻━━┻━━┛
                                    ┃┃╋╋╋╋╋╋┃┃
                                    ┗┛╋╋╋╋╋╋┗┛

```

# prepCode
🏔️ Preparation code for synthetic seismic data traces, that mimics real ones 🌎

PrepCode (preparation Code) is aimed to mimic real seismic data traces.
The code input is synthetic raw velocity seismogram (raw data) in SAC format.
Preclude output is converted to a Mini-SEED (MSEED) format, own
Stream of Integers, contains all the traces, ready to be replayed in 
the Israeli's Earthquake Early Warning (EEW) algorithm - EPIC.
PrepCode uses EPIC minimum velocity amplitude check (Pv), for determining the estimated P arrival for the station. 

The default amplitude check:
![equation](https://latex.codecogs.com/svg.image?Pv=1e-5.5\&space;cm/sec&space;\quad&space;\mathbf{or}\quad3.16e-8\&space;m/sec^2)[^1].

[^1]:
      please see: Chung, A. I., I. Henson, and R. M. Allen, 2019, Optimizing Earthquake Early Warning Performance: ElarmS-3, Seismological Researc    Letters, 90, no. 2A, 727–743, doi:10.1785/0220180192.

### The main code steps:

- reading raw data traces, with partial sample rate. 
- the raw data is converted to acceleration (m/sec**2) and resampled to whole numbers (40 Hz as default)
- first white noise adding, 110dB (relative to acceleration) and 120 sec long
- second white noise adding, before P arrival
- the re-processed seismogram's are multiplayed by gain factor (1e7 default)
- the final prepCode valuus are seismic acceleration data traces, with stream of
integers units (Counts).
   

   
### Setup
1. - [ ] clone the prepCode repository
2. - [ ] install the dependencies:
     - [ ] numpy 
     - [ ] matplotlib
     - [ ] obspy 
     - [ ] pandas
     - [ ] glob
3. - [ ] make sure you got the right stations.d file, contains the columns: lat, lon and station name 
4. - [ ] before running the code, update the channels file in the early warning algorithm to m/sec**2 units
5. - [ ] enter script.ipynb notebook for more information 🎉

### Credits

prepCode relies on research with Ben-Gurion University of the Negev and Geological Survey of Israel. My thanks to Dr. Ran Nof and Professor Michael Tsesarsky for participating in this process.

### License
*Copyright (c) 2022 by Almog Blaer*.
prepCode is released under the GNU Lesser General Public License version 3 or any later version. See LICENSE.TXT for full details.
