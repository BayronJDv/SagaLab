from flask import Flask, request, jsonify
import random

app = Flask(__name__)

# Base de datos en memoria
doctores = [
    {
        "id": 1,
        "nombre": "Dr. García",
        "especialidad": "cardiologia",
        "disponible": True,
    },
    {
        "id": 2,
        "nombre": "Dr. Pérez",
        "especialidad": "neurocirugia",
        "disponible": True,
    },
    {
        "id": 3,
        "nombre": "Dra. Ruiz",
        "especialidad": "traumatologia",
        "disponible": False,
    },
    {
        "id": 4,
        "nombre": "Dr. López",
        "especialidad": "cirugia general",
        "disponible": True,
    },
    {
        "id": 5,
        "nombre": "Dra. Torres",
        "especialidad": "cirugia general",
        "disponible": True,
    },
]

# Asignaciones exitosas (para rollback)
asignaciones_exitosas = []


@app.route("/assign", methods=["POST"])
def assign_doctor():
    data = request.get_json()
    patient_id = data.get("patient_id")
    surgery_type = data.get("surgery_type", "").lower()

    # Buscar doctores disponibles de la especialidad
    disponibles = [
        d for d in doctores if d["especialidad"] == surgery_type and d["disponible"]
    ]

    if not disponibles:
        return jsonify(
            {"message": f"No hay doctores disponibles para {surgery_type}"}
        ), 400

    # Elegir uno al azar
    doctor = random.choice(disponibles)
    doctor["disponible"] = False  # marcar como ocupado
    asignaciones_exitosas.append({"patient_id": patient_id, "doctor_id": doctor["id"]})

    print(f"🩺 Doctor {doctor['nombre']} asignado al paciente {patient_id}")
    return jsonify(
        {
            "message": f"Doctor {doctor['nombre']} asignado correctamente",
            "doctor_id": doctor["id"],
            "especialidad": doctor["especialidad"],
        }
    ), 200


@app.route("/cancel", methods=["POST"])
def cancel_assignment():
    data = request.get_json()
    patient_id = data.get("patient_id")

    asignacion = next(
        (a for a in asignaciones_exitosas if a["patient_id"] == patient_id), None
    )

    if not asignacion:
        return jsonify(
            {"message": f"No hay asignación activa para el paciente {patient_id}"}
        ), 404

    # Revertir
    doctor_id = asignacion["doctor_id"]
    doctor = next((d for d in doctores if d["id"] == doctor_id), None)
    if doctor:
        doctor["disponible"] = True
        asignaciones_exitosas.remove(asignacion)
        print(
            f"❌ Asignación cancelada para paciente {patient_id} (Doctor {doctor['nombre']})"
        )
        return jsonify(
            {"message": f"Asignación cancelada para paciente {patient_id}"}
        ), 200

    return jsonify({"message": "Doctor no encontrado para cancelar"}), 404


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "doctor-assignment"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
