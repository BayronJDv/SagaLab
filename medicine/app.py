from flask import Flask, request, jsonify

app = Flask(__name__)

# Base de datos en memoria
hospital_medicamentos = {
    "Atenolol",
    "Heparina",
    "Nitroglicerina",
    "Amoxicilina",
    "Ibuprofeno",
    "Paracetamol",
    "Ceftriaxona",
    "Omeprazol",
    "Furosemida",
    "Insulina",
}

# Registro de reservas activas
reservas_activas = {}

# Requerimientos por tipo de cirugía
requerimientos_por_cirugia = {"cardiology": {"Atenolol", "Heparina", "Nitroglicerina"}}


@app.route("/reserve", methods=["POST"])
def reserve_medicamentos():
    data = request.get_json()
    patient_id = data.get("patient_id")
    surgery_type = data.get("surgery_type", "").lower()

    if not patient_id or not surgery_type:
        return jsonify({"message": "Datos incompletos"}), 400

    # Verificar si el tipo de cirugía requiere medicamentos específicos
    if surgery_type not in requerimientos_por_cirugia:
        return jsonify(
            {
                "message": f"No se requiere reserva especial de medicamentos para {surgery_type}"
            }
        ), 200

    requeridos = requerimientos_por_cirugia[surgery_type]

    # Verificar disponibilidad
    if not requeridos.issubset(hospital_medicamentos):
        return jsonify(
            {
                "message": f"No hay disponibilidad de todos los medicamentos para {surgery_type}"
            }
        ), 400

    reservas_activas[patient_id] = list(requeridos)
    print(f"💊 Reserva exitosa para paciente {patient_id}: {', '.join(requeridos)}")

    return jsonify(
        {
            "message": f"Medicamentos reservados exitosamente para paciente {patient_id}",
            "reservados": list(requeridos),
        }
    ), 200


@app.route("/cancel", methods=["POST"])
def cancel_reserva():
    data = request.get_json()
    patient_id = data.get("patient_id")

    if patient_id in reservas_activas:
        del reservas_activas[patient_id]
        print(f"❌ Reserva de medicamentos cancelada para paciente {patient_id}")
        return jsonify(
            {"message": f"Reserva cancelada para paciente {patient_id}"}
        ), 200
    else:
        return jsonify({"message": "No hay reserva activa para este paciente"}), 404


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "pharmacy"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006, debug=True)
