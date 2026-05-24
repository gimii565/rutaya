// Utilidades generales de RutaYa

// Actualizar ubicación del usuario en el servidor
function updateLocation(lat, lng) {
    fetch('/api/location/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
        },
        body: JSON.stringify({ latitude: lat, longitude: lng })
    });
}

// Obtener ubicación del conductor asignado
function getDriverLocation(tripId, callback) {
    fetch(`/api/location/driver/${tripId}`)
        .then(res => res.json())
        .then(data => callback(data));
}

// Obtener ubicación de un pasajero
function getPassengerLocation(tripId, callback) {
    fetch(`/api/location/passenger/${tripId}`)
        .then(res => res.json())
        .then(data => callback(data));
}

// Iniciar seguimiento de ubicación en tiempo real
function startLocationTracking() {
    if (navigator.geolocation) {
        navigator.geolocation.watchPosition(
            position => {
                updateLocation(
                    position.coords.latitude,
                    position.coords.longitude
                );
            },
            error => console.log('Error de geolocalización:', error),
            { enableHighAccuracy: true, maximumAge: 5000, timeout: 10000 }
        );
    }
}