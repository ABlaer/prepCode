
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

prepCode (preparation Code) is aimed to mimic real seismic data traces.
The code input are synthetic raw velocity seismogram (raw data) in SAC foramt.
prepCode output converts the raw data to Mini-SEED (MSEED) format, own
stream of integers seismic data, contains all the traces, ready to be replay in 
the Israeli Earthquake Early Warning (EEW) algorithm - EPIC.
prepCode uses EPIC minimum velocity amplitude check (Pv), for determine the estimated P
arrival for the station. 

![equation](https://latex.codecogs.com/svg.image?Pv=1e-5.5\&space;cm/sec&space;\quad&space;\mathbf{or}\quad3.16e-8\&space;m/sec^2)[^1].

[^1]:
      please see: Chung, A. I., I. Henson, and R. M. Allen, 2019, Optimizing Earthquake Early Warning Performance: ElarmS-3, Seismological Researc    Letters, 90, no. 2A, 727–743, doi:10.1785/0220180192.

### The main code steps:

- reading raw data traces, with 67.31 Hz sample rate 
- the raw data is converted to acceleration (m/sec**2) and resampled to 40 Hz
- first white noise adding, 110dB (relative to acceleration) and 120 sec long
- second white noise adding, before P arrival
- the re-processed seismogram's are multilayered by a gain factor (1e7 default)
- the final prepCode value product is seismic acceleration data traces, with stram of
   integers units (counts).
   

   
### Set-up
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
prepCode relies on research with  Ben-Gurion University of the Negev and Geological Survey of Israel.
I gratefully acknowledge Dr. Ran Nof and Prof. Michael Tsesarsky for taking part in this process. 

### License
*Copyright (c) 2022 by Almog Blaer*.
prepCode is released under the GNU Lesser General Public License version 3 or any later version. See LICENSE.TXT for full details.
