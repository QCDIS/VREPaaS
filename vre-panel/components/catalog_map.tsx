import React from "react";
import {
    Map,
    GeoJSON,
    geoJSON,
    LatLngBounds,
    Polygon,
    Marker,
} from "leaflet";
import { Geometry } from "geojson";
import {
    MapContainer,
    TileLayer,
    useMapEvents,
} from "react-leaflet";
import 'leaflet/dist/leaflet.css';

interface CatalogMapProps{
    vlab_slug?: string;
}

const CatalogMap: React.FC<CatalogMapProps> = ({vlab_slug}) => {

    async function get_features(api_endpoint: String, bounds: LatLngBounds) {
        const url = `${api_endpoint}/?format=json&in_bbox=${bounds.toBBoxString()}&vlab_slug=${vlab_slug}`;
        const requestOptions: RequestInit = {
            method: "GET",
            headers: {
                'Content-Type': 'application/json',
            }
        };
        const res = await fetch(url, requestOptions);
        console.log(res)
        return res.json();
    }

    async function render_features(map: Map) {
        map.eachLayer((layer)=>{
            if (
              (layer instanceof Polygon)
              || (layer instanceof Marker)
            )
            {
                layer.remove();
            }
        });

        let geo_json: GeoJSON<any, Geometry>

        function highlightFeature(e) {
            let layer = e.target;
            layer.setStyle({
                weight: 5,
                color: '#669',
                fillOpacity: 0.7,
            });
        }

        function resetHighlight(e) {
            geo_json.resetStyle(e.target);
        }

        function onEachFeature(feature, layer) {
            layer.on({
                mouseover: highlightFeature,
                mouseout: resetHighlight,
            });
            layer.bindPopup(feature.properties.title);
        }

        geo_json = geoJSON(null, {onEachFeature});
        geo_json.addTo(map);

        const url = process.env.NEXT_PUBLIC_ENV_VRE_API_URL;
        get_features(`${url}/geodataprods`, map.getBounds()).then((d) =>geo_json.addData(d));
    }

    function CallbackHooks() {
        const map = useMapEvents({
            moveend: () => render_features(map),
        });
        return null;
    }

    return (
        <MapContainer
            id="map"
            center={[50, 10]} zoom={3.5}
            style={{height: "100%", width: "100%"}}
            whenCreated={render_features}
        >
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <CallbackHooks/>
        </MapContainer>
    )
}

export default CatalogMap