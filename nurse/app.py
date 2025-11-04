from flask import Flask, request, jsonify

app = Flask(__name__)

# Base de datos en memoria: enfermeros disponibles por turno
nursing_staff = {
    "morning": ["Ana", "Carlos"],
    "evening": ["Beatriz", "David"],
    "night": ["Elena"],
}

# Asignaciones registradas
assignments = []


@app.route("/assign", methods=["POST"])
def assign_nurse():
    data = request.get_json()
    patient_id = data.get("patient_id")
    shift = data.get("shift", "morning")

    if not patient_id:
        return jsonify({"message": "Missing patient_id"}), 400

    available = nursing_staff.get(shift, [])
    if not available:
        return jsonify({"message": f"No nurses available for {shift} shift"}), 400

    # Asignar el primer enfermero disponible
    nurse = available.pop(0)
    assignment = {"patient_id": patient_id, "nurse": nurse, "shift": shift}
    assignments.append(assignment)

    return jsonify(
        {
            "message": f"Nurse {nurse} assigned to patient {patient_id} for {shift} shift",
            "assignment": assignment,
        }
    ), 200


@app.route("/cancel", methods=["POST"])
def rollback_assignment():
    data = request.get_json()
    patient_id = data.get("patient_id")

    if not patient_id:
        return jsonify({"message": "Missing patient_id"}), 400

    # Buscar la última asignación del paciente
    for assignment in reversed(assignments):
        if assignment["patient_id"] == patient_id:
            assignments.remove(assignment)
            # Devolver al enfermero a su turno
            nursing_staff[assignment["shift"]].append(assignment["nurse"])
            return jsonify(
                {
                    "message": f"Assignment for patient {patient_id} rolled back",
                    "restored_nurse": assignment["nurse"],
                }
            ), 200

    return jsonify({"message": f"No assignment found for patient {patient_id}"}), 404


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "service": "nursing"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5008)
