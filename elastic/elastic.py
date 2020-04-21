import datetime


ELASTIC_HOST = "localhost"
ELASTIC_PORT = 9200
DATA_INDEX = "parking-data"
DOCUMENT_TYPE = "parking-place"


def export_elastic(meta_data, place_ids, rows):
    from elasticsearch import Elasticsearch

    es = Elasticsearch([{
        "host": ELASTIC_HOST,
        "port": ELASTIC_PORT
    }])

    for place_idx, place_id in enumerate(sorted(place_ids)):
        print(f"{place_idx+1}/{len(place_ids)}: exporting {place_id}")

        place_data = meta_data.get(place_id) or {}

        num_all = None
        if place_data.get("num_all"):
            num_all = int(place_data["num_all"])

        for i, row in enumerate(rows):
            value = row.get(place_id)
            if value:
                timestamp = datetime.datetime.strptime(row["timestamp"][:19], "%Y-%m-%dT%H:%M:%S")
                num_free = int(value)
                percent_free = None

                if num_all:
                    percent_free = round(num_free / num_all * 100, 3)

                document = {
                    "timestamp": timestamp,
                    "place_id": place_id,
                    "num_free": num_free,
                    "num_all": num_all,
                    "percent_free": percent_free,
                    "city_name": place_data.get("city_name"),
                    "place_name": place_data.get("place_name"),
                }

                es.index(
                    index="parking-data",
                    doc_type="parking-place",
                    body=document,
                )
