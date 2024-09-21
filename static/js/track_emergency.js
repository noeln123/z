document.addEventListener('DOMContentLoaded', () => {
    const emergencyId = document.getElementById('emergency-id').value;
    const emergencyStatus = document.getElementById('emergency-status').value;
    const initialLatitude = 21.0278; // TP.HCM
    const initialLongitude = 105.8342;
    let userPos;
    let routingControl;
    let hasReceivedAmbulanceLocation = false;

    console.log(emergencyStatus);

    // Khởi tạo SocketIO
    const socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // Tham gia vào phòng tương ứng với emergencyId
    socket.on('connect', () => {
        console.log(`emergency_${emergencyId}`);
        socket.emit('join_room', { 'room': `emergency_${emergencyId}` });
    });

    if (emergencyStatus !== "Pending") {
        var map = L.map('map').setView([initialLatitude, initialLongitude], 16);

        var ambulanceIcon = L.icon({
            iconUrl: ambulanceIconUrl,
            iconSize: [50, 50]
        });
        var userIcon = L.icon({
            iconUrl: userIconUrl, 
            iconSize: [80, 80]
        });

    
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);

        var userMarker = L.marker([initialLatitude, initialLongitude], {
            title: "User",
            icon: userIcon
        }).addTo(map);

        var ambulanceMarker = L.marker([initialLatitude, initialLongitude], {
            title: "Ambulance",
            icon: ambulanceIcon
        }).addTo(map);

        navigator.geolocation.watchPosition(position => {
            userPos = [position.coords.latitude, position.coords.longitude];
            if (hasReceivedAmbulanceLocation) {
                map.fitBounds([userPos, ambulanceMarker.getLatLng()]);
            } else {
                map.setView(userPos, 16); 
            }
            
            userMarker.setLatLng(userPos);

        }, (error) => {
            console.error('Geolocation error:', error);
        }, {
            enableHighAccuracy: true,  
            timeout: 10000,            
            maximumAge: 0              
        });

        socket.on('location_update', (data) => {
            console.log("Cập nhật vị trí");
            const { latitude, longitude } = data;
            updateMarker(latitude, longitude);
            hasReceivedAmbulanceLocation = true; 
        });
    }

    socket.on('status_update', (data) => {
        console.log("Status update received:", data.status);
        updateStatusBadge(data.status);
    });

    socket.on('joined_room', (data) => {
        console.log("joined room:", data);
    });

    socket.on('error', (data) => {
        console.error('Error:', data.message);
    });

    function updateMarker(lat, lng) {
        ambulanceMarker.setLatLng([lat, lng]);
        map.fitBounds([userPos, [lat, lng]]);
        calculateAndDisplayRoute(userPos, [lat, lng])
    }

    function updateStatusBadge(newStatus) {
        const statusBadge = document.getElementById('status-badge');
        if (statusBadge) {
            statusBadge.className = 'badge ';
            
            switch (newStatus) {
                case 'Pending':
                    statusBadge.classList.add('bg-warning', 'text-dark');
                    break;
                case 'Dispatched':
                    location.reload();
                    break;
                case 'On the way':
                    statusBadge.classList.add('bg-primary');
                    break;
                case 'Arrived':
                    statusBadge.classList.add('bg-success');
                    break;
                case 'Transporting':
                    statusBadge.classList.add('bg-secondary');
                    break;
                default:
                    statusBadge.classList.add('bg-dark');
                    break;
            }

            statusBadge.textContent = newStatus;
        }
    }


    function calculateAndDisplayRoute(userPos, carPos) {
        if (routingControl) {
            map.removeControl(routingControl);
        }

        routingControl = L.Routing.control({
            waypoints: [
                L.latLng(carPos[0], carPos[1]),
                L.latLng(userPos[0], userPos[1])
            ],
            router: L.Routing.osrmv1({
                language: 'en',
                profile: 'car'
            }),
            lineOptions: {
                styles: [{ color: 'red', opacity: 1, weight: 5, className: 'blinking-route' }]
            },
            createMarker: function() { return null; },
            addWaypoints: false,
            routeWhileDragging: false,
            draggableWaypoints: false,
            fitSelectedRoutes: true,
            showAlternatives: false,
            show: false
        }).on('routesfound', function(e) {
            const routes = e.routes;
            const summary = routes[0].summary;

            const distance = summary.totalDistance / 1000; 
            const estimatedTime = Math.round(summary.totalTime / 60);
            const distanceElem = document.getElementById('distance-to-ambulance');
            distanceElem.textContent = '('+distance.toFixed(2) + ' km ~ ';

            const estimatedTimeElem = document.getElementById('estimated-time');
            estimatedTimeElem.textContent = estimatedTime + ' minutes)';

        }).addTo(map);

        document.querySelectorAll('.leaflet-routing-container').forEach(function(el) {
            el.style.display = 'none';
        });
    }
});
