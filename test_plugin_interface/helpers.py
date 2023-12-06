from typing import List

import requests
import geopandas as gpd

from .osm2geojson import json2geojson

_OVERPASS_URL = "http://overpass-api.de/api/interpreter"


def _build_city_road_network_overpass_query(city_name: str, selected_tag_values: List[str]) -> str:
    reg_ex = "|".join(selected_tag_values)
    return f"""
    [out:json];
    area["name"="{city_name}"]->.a;
    way(area.a)["highway"~"{reg_ex}"];
    out geom;
    """


def _build_city_buildings_overpass_query(city_name: str, selected_tag_values: List[str]) -> str:
    reg_ex = "|".join(selected_tag_values)
    return f"""
    [out:json];
    area["name"="{city_name}"]->.city;
    (
      node(area.city)["building"~"{reg_ex}"];
      way(area.city)["building"~"{reg_ex}"];
      relation(area.city)["building"~"{reg_ex}"];
    );
    out body;
    >;
    out skel qt;
    """


def download_osm_data_as_geojson(overpass_query: str) -> dict:
    response = requests.get(_OVERPASS_URL, params={'data': overpass_query})
    data = response.json()
    geojson_data = json2geojson(data)
    return geojson_data


def download_city_road_network(city_name: str, selected_tag_values: List[str]) -> dict:
    return download_osm_data_as_geojson(
        _build_city_road_network_overpass_query(city_name, selected_tag_values)
    )


def download_city_road_network_as_gdf(city_name: str, selected_tag_values: List[str]) -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame.from_features(download_city_road_network(city_name, selected_tag_values)["features"])


def download_city_buildings(city_name: str, selected_tag_values: List[str]) -> dict:
    return download_osm_data_as_geojson(
        _build_city_buildings_overpass_query(city_name, selected_tag_values)
    )