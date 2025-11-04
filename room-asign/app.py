from flask import Flask, request, jsonify

app = Flask(__name__)

# Base de datos en memoria
rooms = [
    {
        "id": 1,
        "specialty": "cardiologia",
        "usage": {"monday": 1, "tuesday": 0, "wednesday": 0},
    },
    {
        "id": 2,
        "specialty": "appendectomy",
        "usage": {"monday": 0, "tuesday": 0, "wednesday": 0},
    },
    {
        "id": 3,
        "specialty": "neurology",
        "usage": {"monday": 2, "tuesday": 0, "wednesday": 0},
    },
    {
        "id": 4,
        "specialty": "cardiology",
        "usage": {"monday": 0, "tuesday": 0, "wednesday": 0},
    },
]

MAX_USAGE_PER_DAY = 2
reservations = []  # Guardar qué paciente tiene qué sala en qué día


@app.route("/reserve", methods=["POST"])
def reserve_room():
    data = request.get_json()
    patient_id = data.get("patient_id")
    surgery_type = data.get("surgery_type")
    surgery_day = data.get("surgery_day")

    if not all([patient_id, surgery_type, surgery_day]):
        return jsonify({"message": "Datos incompletos"}), 400

    # Buscar sala que cumpla con la especialidad y disponibilidad
    for room in rooms:
        if room["specialty"] == surgery_type:
            current_usage = room["usage"].get(surgery_day, 0)
            if current_usage < MAX_USAGE_PER_DAY:
                # Asignar sala
                room["usage"][surgery_day] = current_usage + 1
                reservations.append(
                    {
                        "patient_id": patient_id,
                        "room_id": room["id"],
                        "day": surgery_day,
                    }
                )
                print(f"✅ Sala {room['id']} asignada al paciente {patient_id}")
                return jsonify(
                    {
                        "message": f"Sala {room['id']} asignada correctamente al paciente {patient_id}"
                    }
                ), 200

    print(f"❌ No hay salas disponibles para {surgery_type} el día {surgery_day}")
    return jsonify(
        {
            "message": f"No hay salas disponibles para {surgery_type} el día {surgery_day}"
        }
    ), 409


@app.route("/cancel", methods=["POST"])
def cancel_reservation():
    data = request.get_json()
    patient_id = data.get("patient_id")

    if not patient_id:
        return jsonify({"message": "Falta patient_id"}), 400

    for res in list(reservations):
        if res["patient_id"] == patient_id:
            # Buscar la sala asignada
            for room in rooms:
                if room["id"] == res["room_id"]:
                    current_usage = room["usage"].get(res["day"], 0)
                    if current_usage > 0:
                        room["usage"][res["day"]] = current_usage - 1
                    reservations.remove(res)
                    print(
                        f"❌ Reserva cancelada para paciente {patient_id}, sala {room['id']}"
                    )
                    return jsonify(
                        {"message": f"Reserva cancelada para paciente {patient_id}"}
                    ), 200

    return jsonify(
        {"message": f"No se encontró reserva activa para paciente {patient_id}"}
    ), 404


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "operating-room"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
