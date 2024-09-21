document.addEventListener('DOMContentLoaded', () => {
    const emergencyId = document.getElementById('emergency-id').value;
    const emergencyStatus = document.getElementById('emergency-status').value;
    const initialLatitude = 21.0278; // Mặc định tọa độ TP.HCM
    const initialLongitude = 105.8342;
    let userPos;
    let routingControl;
    let hasReceivedAmbulanceLocation = false; // Biến cờ để kiểm tra nếu có cập nhật vị trí xe cứu thương

    console.log(emergencyStatus);

    // Khởi tạo SocketIO
    const socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // Tham gia vào phòng tương ứng với emergencyId
    socket.on('connect', () => {
        console.log(`emergency_${emergencyId}`);
        socket.emit('join_room', { 'room': `emergency_${emergencyId}` });
    });

    if (emergencyStatus !== "Pending") {
        // Khởi tạo bản đồ Leaflet
        var map = L.map('map').setView([initialLatitude, initialLongitude], 16);

        var ambulanceIcon = L.icon({
            iconUrl: ambulanceIconUrl, // Đảm bảo rằng URL này được định nghĩa
            iconSize: [50, 50]
        });
        var userIcon = L.icon({
            iconUrl: userIconUrl, // Đảm bảo rằng URL này được định nghĩa
            iconSize: [80, 80]
        });

        // Thêm layer từ OpenStreetMap
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);

        // Thêm marker để biểu thị vị trí xe cứu thương
        var userMarker = L.marker([initialLatitude, initialLongitude], {
            title: "User",
            icon: userIcon
        }).addTo(map);

        var ambulanceMarker = L.marker([initialLatitude, initialLongitude], {
            title: "Ambulance",
            icon: ambulanceIcon
        }).addTo(map);

        // Cập nhật vị trí hiện tại của user
        navigator.geolocation.watchPosition(position => {
            userPos = [position.coords.latitude, position.coords.longitude];
            if (hasReceivedAmbulanceLocation) {
                map.fitBounds([userPos, ambulanceMarker.getLatLng()]);
            } else {
                map.setView(userPos, 16); 
            }
            
            // Đặt marker cho người dùng
            userMarker.setLatLng(userPos);

        }, () => {
            handleLocationError(true, map.getCenter());
        }, {
            enableHighAccuracy: true,  // Yêu cầu vị trí có độ chính xác cao (sử dụng GPS nếu có)
            timeout: 10000,            // Giới hạn thời gian chờ 10 giây để lấy vị trí
            maximumAge: 0              // Không sử dụng vị trí đã lưu trong cache
        });

        // Lắng nghe sự kiện cập nhật vị trí
        socket.on('location_update', (data) => {
            console.log("Cập nhật vị trí");
            const { latitude, longitude } = data;
            updateMarker(latitude, longitude);
            hasReceivedAmbulanceLocation = true; // Đánh dấu rằng đã nhận được vị trí từ xe cứu thương
        });
    }

    // Lắng nghe sự kiện cập nhật trạng thái
    socket.on('status_update', (data) => {
        console.log("Status update received:", data.status);
        updateStatusBadge(data.status);
    });

    // Xử lý lỗi nếu có
    socket.on('error', (data) => {
        console.error('Error:', data.message);
    });

    // Hàm cập nhật marker trên bản đồ
    function updateMarker(lat, lng) {
        ambulanceMarker.setLatLng([lat, lng]);
        map.fitBounds([userPos, [lat, lng]]);
        calculateAndDisplayRoute(userPos, [lat, lng])
    }

    // Hàm cập nhật badge trạng thái
    function updateStatusBadge(newStatus) {
        const statusBadge = document.getElementById('status-badge');
        if (statusBadge) {
            // Loại bỏ các lớp màu hiện tại
            statusBadge.className = 'badge ';
            
            // Thêm lớp màu dựa trên trạng thái mới
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

            // Cập nhật nội dung text
            statusBadge.textContent = newStatus;
        }
    }


    function calculateAndDisplayRoute(userPos, carPos) {
        // Xóa tuyến đường cũ nếu có
        if (routingControl) {
            map.removeControl(routingControl);
        }

        // Sử dụng OSRM cho định tuyến
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

            // Tính toán khoảng cách và thời gian
            const distance = summary.totalDistance / 1000; // Đổi từ mét sang km
            const estimatedTime = Math.round(summary.totalTime / 60); // Thời gian ước tính (phút)

            // Cập nhật phần tử HTML với khoảng cách
            const distanceElem = document.getElementById('distance-to-ambulance');
            distanceElem.textContent = '('+distance.toFixed(2) + ' km ~ ';

            // Cập nhật phần tử HTML với thời gian ước tính
            const estimatedTimeElem = document.getElementById('estimated-time');
            estimatedTimeElem.textContent = estimatedTime + ' minutes)';

        }).addTo(map);

        // Ẩn bảng điều khiển sau khi tạo routing
        document.querySelectorAll('.leaflet-routing-container').forEach(function(el) {
            el.style.display = 'none';
        });
    }
});
