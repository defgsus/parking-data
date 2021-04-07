import datetime

from elastipy import Exporter


class ParkingExporter(Exporter):
    INDEX_NAME = "parking-data"

    MAPPINGS = {
        "properties": {
            "timestamp": {"type": "date"},
            "timestamp_hour": {"type": "float"},
            "timestamp_weekday": {"type": "keyword"},
            "place_id": {"type": "keyword"},
            "num_free": {"type": "integer"},
            "num_all": {"type": "integer"},
            "percent_free": {"type": "float"},
            "city_name": {"type": "keyword"},
            "place_name": {"type": "keyword"},
            "full_name": {"type": "keyword"},
            "location": {"type": "geo_point"},
        }
    }

    def get_document_id(self, data):
        return f"%(place_id)s-%(timestamp)s" % data


def export_elastic(meta_data, place_ids, rows, bulk_size=500, clear_index=False):

    def iter_documents():
        for place_idx, place_id in enumerate(sorted(place_ids)):

            print(f"{place_idx+1}/{len(place_ids)}: exporting {place_id}")

            place_data = meta_data.get(place_id) or {}

            num_all = None
            if place_data.get("num_all"):
                num_all = int(place_data["num_all"])

            for row in rows:
                value = row.get(place_id)
                if value:
                    timestamp = datetime.datetime.strptime(row["timestamp"][:19], "%Y-%m-%dT%H:%M:%S")
                    num_free = int(value)
                    percent_free = None

                    if num_all:
                        percent_free = round(num_free / num_all * 100, 3)

                    document = {
                        "timestamp": timestamp,
                        "timestamp_hour": timestamp.hour + timestamp.minute / 60.,
                        "timestamp_weekday": timestamp.strftime("%w %A"),
                        "place_id": place_id,
                        "num_free": num_free,
                        "num_all": num_all,
                        "percent_free": percent_free,
                        "city_name": place_data.get("city_name"),
                        "place_name": place_data.get("place_name"),
                        "full_name": "%s / %s" % (
                            place_data.get("city_name") or place_id,
                            place_data.get("place_name") or "-",
                        )
                    }
                    if place_data.get("latitude") and place_data.get("longitude"):
                        document["location"] = {
                            "lat": place_data.get("latitude"),
                            "lon": place_data.get("longitude"),
                        }

                    yield document

    exporter = ParkingExporter()
    if clear_index:
        exporter.delete_index()

    exporter.export_list(
        iter_documents(),
        chunk_size=bulk_size,
        verbose=True, count=len(place_ids) * len(rows)
    )
