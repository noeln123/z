# Rapid Rescue

Rapid Rescue is a web application that allows users to quickly request ambulance services, track the real-time location of the ambulance, and provide necessary medical information to Emergency Medical Technicians (EMT).

## Key Features

- User registration and login
- Manage personal profile and medical records
- Request ambulance service
- Real-time ambulance tracking
- Provide feedback on the service
- Admins manage ambulances and drivers
- EMTs access patient information and update status

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/z.git
    cd rapid_rescue
    ```

2. Create and activate a virtual environment:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

4. Configure MySQL in `config.py`.

5. Initialize and apply migration:

    ```bash
    flask db init
    flask db migrate -m "Initial migration."
    flask db upgrade
    ```

6. Run the application:

    ```bash
    python app.py
    ```

## License

MIT License
