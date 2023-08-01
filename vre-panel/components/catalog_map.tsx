import {
    FC,
    useEffect,
    useState,
    useCallback,
} from "react";
import {default as L} from 'leaflet';
import {GeoJsonObject} from 'geojson';
import {
    MapContainer,
    TileLayer,
    GeoJSON,
    useMapEvents,
} from "react-leaflet";
import hash from 'object-hash';
import 'leaflet/dist/leaflet.css';
import getConfig from 'next/config';

interface DataProductsProps {
    map: L.Map;
    vlab_slug?: string | string[];
}

interface CatalogMapProps {
    vlab_slug?: string | string[];
}

const DataProducts: FC<DataProductsProps> = ({map, vlab_slug}) => {

    const { publicRuntimeConfig } = getConfig()

    const [data, setData] = useState<GeoJsonObject>({'type': 'Feature'})
    const [geoJSON, setGeoJSON] = useState<L.GeoJSON | null>(null)

    function keyFunction(obj: any) {
        try {
            return hash(obj)
        } catch (e) {
            console.log('Error encountered in keyFunction', e)
            return ''
        }
    }

    const getFeatures = useCallback(() => {
        const apiUrl = `${window.location.origin}/${publicRuntimeConfig.apiBasePath}`
        let bounds = map.getBounds()
        const url = `${apiUrl}/geodataprods/?format=json&in_bbox=${bounds.toBBoxString()}&vlab_slug=${vlab_slug}`;
        const requestOptions: RequestInit = {
            method: "GET",
            headers: {
                'Content-Type': 'application/json',
            }
        };
        fetch(url, requestOptions).then((res) => {
            res.json().then(setData);
        });
    }, [map, vlab_slug])


    const onEachLayer = useCallback((layer: L.Layer) => {
        const highlightFeature = (e: L.LeafletMouseEvent) => {
            e.target.setStyle({
                weight: 5,
                color: '#669',
                fillOpacity: 0.7,
            });
        }

        const resetHighlight = (e: L.LeafletMouseEvent) => {
            if (geoJSON) {
                geoJSON.resetStyle(e.target);
            }
        }

        layer.on({
            mouseover: highlightFeature,
            mouseout: resetHighlight,
        });
        // @ts-expect-error: geoJSON layers have a feature attribute
        layer.bindPopup(layer.feature.properties.title);
    }, [geoJSON])

    useEffect(() => {
        if (geoJSON) {
            geoJSON.eachLayer(onEachLayer)
        }
    }, [geoJSON, onEachLayer])

    // initial render
    useEffect(getFeatures, [getFeatures])

    useMapEvents({
        moveend: getFeatures,
    });

    return (
      <GeoJSON
        key={keyFunction(data)}
        data={data}
        ref={setGeoJSON}
      >
      </GeoJSON>
    )
}

const CatalogMap: FC<CatalogMapProps> = ({vlab_slug}) => {

    const [map, setMap] = useState<L.Map | null>(null)

    return (
      <MapContainer
        id="map"
        center={[50, 10]} zoom={3.5}
        style={{height: "100%", width: "100%"}}
        ref={setMap}
      >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {map ? <DataProducts map={map} vlab_slug={vlab_slug}/> : null}
      </MapContainer>
    )
}

export default CatalogMap
