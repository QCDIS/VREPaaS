import {
    Map,
    geoJSON,
    LatLngBounds,
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
    console.log(url, requestOptions);
    const res = await fetch(url, requestOptions);
    return res.json();
}

async function render_features(api_endpoint: String, map: Map) {
    const shapes = await get_features(api_endpoint, map.getBounds());
    geoJSON(shapes)
        .bindPopup((layer) => layer.feature.properties.name)
        .addTo(map);
}

function CatalogItems() {
    const url = process.env.NEXT_PUBLIC_ENV_WFS_API_URL;
    const map = useMapEvents({
        moveend: () => {
            render_features(`${url}/shapes`, map);
            render_features(`${url}/markers`, map);
        },
    });
    console.log(map)
    return null
}

const CatalogMap = () => {
  return (
      <MapContainer id="map" center={[52.5, 5]} zoom={8} style={{height: "100%", width: "100%"}}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <CatalogItems/>
      </MapContainer>
  )
}

export default CatalogMap
