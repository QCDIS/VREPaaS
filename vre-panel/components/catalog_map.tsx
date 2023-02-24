import {
    MapContainer,
    TileLayer,
} from "react-leaflet";
import 'leaflet/dist/leaflet.css';


const CatalogMap = () => {
  return (
      <MapContainer id="map" center={[52.5, 5]} zoom={8} style={{height: "100%", width: "100%"}}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
      </MapContainer>
  )
}

export default CatalogMap
