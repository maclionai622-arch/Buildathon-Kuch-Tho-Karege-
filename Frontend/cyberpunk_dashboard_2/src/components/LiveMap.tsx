import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useEffect } from 'react';

// Fix for Leaflet default icon bug in React/Vite
import icon from 'leaflet/dist/images/marker-icon.png';
import iconRetina from 'leaflet/dist/images/marker-icon-2x.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    iconRetinaUrl: iconRetina,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

interface LiveMapProps {
  originCoords: [number, number];
  activeTargetCoords?: [number, number];
  activeTargetType?: "Fastest" | "Safest" | "Safehouse";
}

// Helper component to recenter map when origin changes
const MapRecenter = ({ coords }: { coords: [number, number] }) => {
  const map = useMap();
  useEffect(() => {
    map.setView(coords, map.getZoom());
  }, [coords, map]);
  return null;
};

export const LiveMap = ({ originCoords, activeTargetCoords, activeTargetType }: LiveMapProps) => {
  const getPolylineStyle = () => {
    switch (activeTargetType) {
      case "Fastest":
        return { color: "yellow", weight: 3, dashArray: "10, 10", className: "animate-dash-march" };
      case "Safest":
        return { color: "#ccff00", weight: 4 };
      case "Safehouse":
        return { color: "cyan", weight: 2, dashArray: "5, 5", className: "animate-dash-march" };
      default:
        return { color: "white", weight: 2 };
    }
  };

  return (
    <div className="relative w-full h-[400px] bg-bg-primary rounded-2xl overflow-hidden neon-border">
      <MapContainer 
        center={originCoords} 
        zoom={13} 
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={false}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        />
        
        <MapRecenter coords={originCoords} />

        {/* Origin Marker */}
        <Marker position={originCoords}>
          <Popup>Current Mission Area (Origin)</Popup>
        </Marker>

        {/* Active Target Marker & Polyline */}
        {activeTargetCoords && (
          <>
            <Marker position={activeTargetCoords}>
              <Popup>Active Target: {activeTargetType}</Popup>
            </Marker>
            <Polyline 
              positions={[originCoords, activeTargetCoords]} 
              {...getPolylineStyle()}
            />
          </>
        )}
      </MapContainer>
    </div>
  );
};
