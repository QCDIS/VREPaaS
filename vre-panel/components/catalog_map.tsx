import {
    Map,
    geoJSON,
    LatLngBounds,
    Polygon,
    Marker,
} from "leaflet";
import {
    MapContainer,
    TileLayer,
    useMapEvents,
} from "react-leaflet";
import 'leaflet/dist/leaflet.css';

async function get_features(api_endpoint: String, bounds: LatLngBounds) {
    const url = `${api_endpoint}/?format=json&in_bbox=${bounds.toBBoxString()}`;
    const requestOptions: RequestInit = {
        method: "GET",
        headers: {
            'Content-Type': 'application/json',
        }
    };
    const res = await fetch(url, requestOptions);
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

    const geo_json = geoJSON()
    geo_json.bindPopup((layer) => layer.feature.properties.name);
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

const CatalogMap = () => {
    return (
        <MapContainer
            id="map"
            center={[52.5, 5]} zoom={8}
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
