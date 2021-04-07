### historic archive of free parking places across germany

This repository contains the export of 
[parking-scraper](https://github.com/defgsus/parking-scraper) as CSV files.

Data gathering has started 2020/03/24 and this repository is updated daily.

Each day is stored in a single file in the `./csv` directory with the following layout:
```
timestamp                 | place_id1 | place_id2 | ...
2020-03-24T16:00:04+00:00 | 100       | 2         |
2020-03-24T16:01:02+00:00 | 99        |           |
2020-03-24T16:02:03+00:00 |           | 3         |
```

### export

You can use `export.py` to bundle them into a single file.

For example:

```shell script
# install some helper
pip install -r requirements.txt

# export everything and print to console
python export.py

# export everything to a file called everything.csv
python export.py -o everything.csv

# export first April
python export.py -d 2020-04-01

# export everything from April and May
python export.py -d 2020-04 2020-05

# export only parking places where ID contains muenster or ulm
python export.py -p muenster ulm
```
Generally **-d** and **--p** options accept multiple regular expressions separated 
by space which are *OR*-combined.


### export to elasticsearch

```shell script
# install elasticsearch requirements
pip install -r elastic/requirements.txt
```

Then use 
```shell script
python export.py -f elasticsearch
```
to commit each data point to the elasticsearch API. 

The configuration for the server host is currently hardwired to 
default **localhost:9200**. The index name is **parking-data**.

Check the [elastic/elastic.py](elastic/elastic.py) file to see the data structure.


### data structure

Each line in the CSV files contains a timestamp of the recording as *Universal Time Code* 
followed by the free parking spaces of each parking place/lot. An empty column means either 
that there was no change in data since the last timestamp or there was no recording 
because the website or the scraper went down.

For example, most of 2020/03/28 and 29 is missing. 

Free places are generally recorded every 15 minutes 
and every 5 minutes during the period of 6:00 to 20:00 (Europe/Berlin)

The header of each column contains the **place_id** which is just some unique ID 
to identify the parking lot.


### meta data structure

The meta-data for each parking place can be found in `meta-data.csv`. 
The rows **always** contain

- **place_id**: unique ID of the parking lot
- **place_name**: human readable name of parking lot
- **city_name**: Name of city
- **source_id**: unique ID of the source of the data
- **source_web_url**: website of the source of the data

and might contain if known:

- **num_all**: number of total parking places
- **address**: multiline string with address
- **latitude** and **longitude**: geo coordinates
- **place_url**: website for the parking place

Although it must be admitted that the meta data is not maintained with great care. 


### License

I do not really know. I'd argue it's free to use by everyone for everything ... *reasonable*
