
Copyright (C) by Almog Blaer 

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
🏔️ Preparation code for synthetic seismic data traces, that mimic real ones 🌎

prepCode (preparation Code) is aimed to mimic real seismic data traces.
The code input are synthetic raw velocity seismogram (raw data) in SAC foramt.
prepCode output converts the raw data to Mini-SEED (MSEED) format, own
stream of integers seismic data, contains all the traces, ready to be replay in 
the Israeli Earthquake Early Warning (EEW) algorithm - EPIC.
prepCode uses EPIC minimum velocity amplitude check (Pv), for determine the estimated P
arrival for the station. 

Pv value is 1e-5.5 cm/sec or 3.16e-8 m/sec**2 [^1]

### The main code steps:

- reading raw data traces, with 67.31 Hz sample rate 
- the raw data is converted to acceleration (m/sec**2) and resampled to 40 Hz
- first white noise adding, 110dB (relative to acceleration) and 120 sec long
- second white noise adding, before P arrival
- the re-processed seismogram's are multilayered by a gain factor (1e7 default)
- the final prepCode value product is seismic acceleration data traces, with stram of
   integers units (counts).
   
   [^note] please see: Chung, A. I., I. Henson, and R. M. Allen, 2019, Optimizing Earthquake Early Warning Performance: ElarmS-3, Seismological Researc Letters, 90, no. 2A, 727–743, doi:10.1785/0220180192.
   
### Set-up
-[] clone the prepCode repository
-[] 
-[] make sure you got the right stations.d file, with contains lat, lon and station name data
-[] 

see script.ipynb jupyter notebook

### Credits

### License
