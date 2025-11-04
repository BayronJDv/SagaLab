from flask import Flask, request, jsonify

app = Flask(__name__)

# 🧠 Base de datos en memoria: unidades de sangre disponibles por tipo
blood_inventory = {
    "O+": 10,
    "O-": 5,
    "A+": 7,
    "A-": 4,
    "B+": 6,
    "B-": 3,
    "AB+": 2,
    "AB-": 1,
}

# 🩺 Historial de reservas realizadas (para poder revertir)
reservations = {}


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "blood-bank"}), 200


# ✅ Reservar unidades de sangre
@app.route("/reserve", methods=["POST"])
def reserve_blood():
    data = request.get_json()
    patient_id = data.get("patient_id")
    blood_type = data.get("blood_type")
    blood_units = data.get("blood_units")

    if not all([patient_id, blood_type is not None, blood_units is not None]):
        return jsonify({"status": "error", "message": "Datos incompletos"}), 400

    # Normalizar tipo de sangre (por si llega en minúsculas o con espacios)
    blood_type = str(blood_type).strip().upper()

    # Validar existencia del tipo de sangre
    if blood_type not in blood_inventory:
        return jsonify(
            {
                "patient_id": patient_id,
                "status": "error",
                "message": f"Tipo de sangre {blood_type} no disponible",
            }
        ), 404

    # Verificar disponibilidad
    available_units = blood_inventory[blood_type]
    if available_units < blood_units:
        return jsonify(
            {
                "patient_id": patient_id,
                "status": "not_available",
                "message": f"No hay suficientes unidades ({available_units} disponibles, {blood_units} requeridas)",
            }
        ), 400

    # Reservar unidades
    blood_inventory[blood_type] -= blood_units
    reservations[patient_id] = {"blood_type": blood_type, "blood_units": blood_units}

    return jsonify(
        {
            "patient_id": patient_id,
            "status": "reserved",
            "message": f"Reservadas {blood_units} unidades de sangre tipo {blood_type}",
        }
    ), 200


# 🔁 Cancelar reserva (rollback)
@app.route("/cancel", methods=["POST"])
def cancel_reservation():
    data = request.get_json()
    patient_id = data.get("patient_id")

    if patient_id not in reservations:
        return jsonify(
            {"status": "error", "message": "No hay reserva previa para este paciente"}
        ), 404

    # Recuperar datos de la reserva y devolver unidades
    reservation = reservations.pop(patient_id)
    blood_type = reservation["blood_type"]
    blood_units = reservation["blood_units"]

    blood_inventory[blood_type] += blood_units

    return jsonify(
        {
            "patient_id": patient_id,
            "status": "canceled",
            "message": f"Reserva cancelada y {blood_units} unidades devueltas al inventario ({blood_type})",
        }
    ), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5007)
