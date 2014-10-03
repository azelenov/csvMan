<<<How to make a report>>>
INSTALL
1. Install ant. Add it to path.
2. Add python to path.

PROCESSING
1. Add your files to input folder. The names must be the same as in build.xml file.
Common case is delete date prefix in each file.
2. Open console in csvMan folder
3. Write  "ant"  and press ENTER.
4. Wait BUILD_SUCCESSFUL message. For big data this could be a long time for "split" phase.
If build failed make recheck names and close all opened csv files.

CREATING AN REPORT
1. Go to report folder and open stats_tmp.xlsx. Save as file with new name.
2. For each collection(csv file) in folder "key_dist_frequency"
open with excel and copy and paste for each tab to table (marked as #1)
3. For each collection(csv file) in folder "key_count_frequency"
open with excel and copy and paste for each tab to table (marked as #2)
4. For each collection(csv file) in folder "key_count_average"
open with excel and copy and paste for each tab to table (marked as #3)
--AggregatedStatistics tab--
5. Paste from "aggregated_results/key_count%Average..." data to table "Average latency" column (marked as #4)
6. Paste from "aggregated_results/multiple%Statistics..." all data to table (marked as  #5)
7. Paste from "aggregated_results/multiple%Ranges..." all data to table (marked as #6)
7b. If ranges was incorrect, change in build.xml <target name="ranges"> ranges that would be better.

FORMATTING
1. Make sure graphs appeared.
2. Make sure that graphs use all the data from your inserted tables. If not extend graphs data area.
3. Make each table header bold.

FINAL
1. Save a template file with new name.
2. Copy file to moe.
3. Send a link for this file for the team.




