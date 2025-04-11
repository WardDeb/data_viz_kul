# data_viz_kul

## How to run

  > clone repo  
  > pip install .  
  > marimo run marimo

## Project - pig feeding

Dataset is available via [mendeley](https://data.mendeley.com/datasets/2mbw72m3g8/1). 
More specifically, file 'Exp1 (dec2020-feb2021)/Exp1 - Feeding data.csv' is used (and available under the repo under the raw_data folder as a gz'ed file).

## Data explanation
Directly taken from the relevant [mendeley readme](https://data.mendeley.com/datasets/2mbw72m3g8/1/files/31b15858-af92-41e7-84e2-160f04487f65).

This README describes the datasets 'Exp? - Feeding data.csv', which contain records of pig visits to IVOG electronic feeding stations (EFSs).
Datasets are available for four rounds of pigs, each with 10 pens. Each pen contained one IVOG EFS, to which a maximum of 11 pigs had access.
IVOG EFSs register each visit to the feeder, along with pig RFID number and time stamp and trough weight upon entry and exit.
These data were transferred to us on a weekly basis, via the TU Eindhoven, in .DAT format.
The .DAT files are no longer stored, but the csv files described here are their merged equivalents; i.e. no processing has been done beyond merging the daily .DAT files together with the correct date. In addition, feeding rate was calculated, the hour upon which the visit started was extracted, the visit duration was put in a more convenient format (i.e. from 'min.s' to 's'), and empty columns were removed (see 'NOTES' below).

A description of the variables, from left to right, is found below.
- date: The date upon which the feeder visit occurred, in day/month/year.
- tattoo: The tattoo number of the pig, as was linked to its RFID number.
- pig: The RFID number of the pig visiting the feeder. Generally 12 digits, though in round 3 pigs only had 1-3 digits and the column was renamed as 'pig.short'.
- station: The ID number of the IVOG station that recorded the visit, from 1-10. This corresponds with the pen the pig was in; see the powerpoint file that gives the floorplan of the barn.
- weight_start: The weight of the feed in the trough (in kg) at the start of the visit. 
- weight_end: The weight of the feed in the trough (in kg) at the end of the visit. 
- intake: The difference in the weight of the feed in the trough between the end and start of the visit. See notes below for some details surrounding feeder fillings.
- start: The time upon which the visit started, in 'day/month/year hour:minute:second'
- end: The time upon which the visit ended, in 'day/month/year hour:minute:second'
- hour: The hour within which the visit started, i.e. '11' means the visit started between 11:00:00 and 11:59:59.
- duration: The time difference (in seconds) between the visit end and start.
- rate: Column intake divided by column duration, multiplied by 1000 (in kg/s)

NOTES:
- IVOG EFS add about 600 g of feed to the trough when the trough weight goes below a certain limit (not sure what the limit is). This is generally registered as a visit with an intake of -0.6, and with 'FILLING' in column 'tattoo'.
- Some visits with pig (RFID) number 0 were pre-marked as 'FILLING' or 'GHOST', i.e. trough fillings or pig visits lacking an RFID registration, respectively. Reasons/Rules for this are unknown to the authors.
- DO NOT OVERWRITE feed intakes with manually calculated measures. These are incorrect if a pig's feeder visit started during a feeder filling, as then the average filling size of the previous 10 fillings was deducted from the feed intake.
- 'rate' and 'hour' were added by Jacinta; they were not present in the .DAT files.
- There were also some empty columns in the .DAT files, which were removed.
- In the original .DAT file, the 'duration' column was given in the unit 'min.s'. This was turned into seconds by extracting all digits before '.', multiplying these by 60, and adding all digits after '.'.
- In experiment 3, mice were nesting beneath the IVOG load cells and chewed through the cables. This led to missing/unreliable data for station 8 from 09-07-2022 to 22-07-2022 (evening) and for station 9 from 11-06-2022 to 24-06-2022 (18:15h).
- For a few stations, pigs were registered that were not present in the pen (i.e. more than 11 unique pigs were detected). These were pigs in neighbouring pens that were wrongfully registered. Can be corrected using the 'Pig registration' csv's.


These data were never really used directly (and shouldn't be!), but were first checked, cleaned and processed.
An example of such a processing algorithm we published at:
- J.D. Bus, I.J.M.M. Boumans, E.A.M. Bokkers (2023). An algorithm to process, clean and aggregate the data from IVOG electronic feeding stations, Mendeley Data. DOI: 10.17632/tx567ttgyk.1
