from flask import Flask, request, jsonify

app = Flask(__name__)

# Capacidad fija por tipo de sala
CAPACIDAD = {
    "icu": 2,  # Máximo 2 pacientes por día
    "recovery": 3,  # Máximo 3 pacientes por día
}

# Base de datos en memoria: reservas[day][room_type] = [lista de IDs de pacientes]
reservas = {}


@app.route("/reserve", methods=["POST"])
def reserve_room():
    data = request.get_json()
    patient_id = data.get("patient_id")
    room_type = data.get("room_type")
    surgery_day = data.get("surgery_day")

    if not patient_id or not room_type or not surgery_day:
        return jsonify({"message": "Datos incompletos"}), 400

    if room_type not in CAPACIDAD:
        return jsonify({"message": f"Tipo de sala '{room_type}' no válido"}), 400

    # Inicializar el día si no existe
    if surgery_day not in reservas:
        reservas[surgery_day] = {"icu": [], "recovery": []}

    # Inicializar tipo si no existe (por seguridad)
    reservas[surgery_day].setdefault(room_type, [])

    # Verificar si el paciente ya tiene una reserva ese día (para evitar duplicados)
    if patient_id in reservas[surgery_day][room_type]:
        return jsonify(
            {
                "message": f"El paciente {patient_id} ya tiene una reserva en {room_type} el {surgery_day}"
            }
        ), 400

    # Verificar disponibilidad
    ocupadas = reservas[surgery_day][room_type]
    if len(ocupadas) >= CAPACIDAD[room_type]:
        return jsonify(
            {
                "message": f"No hay disponibilidad en la sala {room_type} para el día {surgery_day}"
            }
        ), 400

    # Reservar sala
    ocupadas.append(patient_id)
    print(
        f"🏥 Sala {room_type} reservada para paciente {patient_id} el día {surgery_day}"
    )

    return jsonify(
        {
            "message": f"Sala {room_type} reservada exitosamente para paciente {patient_id} el día {surgery_day}",
            "room_type": room_type,
            "day": surgery_day,
        }
    ), 200


@app.route("/cancel", methods=["POST"])
def cancel_reserva():
    data = request.get_json()
    patient_id = data.get("patient_id")

    for day, tipos in reservas.items():
        for room_type, pacientes in tipos.items():
            if patient_id in pacientes:
                pacientes.remove(patient_id)
                print(
                    f"❌ Reserva cancelada para paciente {patient_id} en {room_type} ({day})"
                )
                return jsonify(
                    {
                        "message": f"Reserva cancelada para paciente {patient_id} en {room_type} el día {day}"
                    }
                ), 200

    return jsonify({"message": "No se encontró reserva para cancelar"}), 404


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "postop_room"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5009, debug=True)
