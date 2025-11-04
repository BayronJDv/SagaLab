from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# URLs de los microservicios (DNS de Kubernetes)
# Si se necesita probar en local cambiar las URLs por localhost y el puerto correspondiente
PATIENT_VALIDATION_URL = "http://patient_validation:5001"
DOCTOR_ASSIGNMENT_URL = "http://doctor_assignment:5002"
OPERATING_ROOM_URL = "http://operating_room:5003"
ANESTHESIA_URL = "http://anesthesia:5004"
LAB_TESTS_URL = "http://lab_tests:5005"
PHARMACY_URL = f"http://pharmacy:5006"
BLOOD_BANK_URL = f"http://blood_bank:5007"
NURSING_STAFF_URL = f"http://nurse:5008"
POSTOP_ROOM_URL = f"http://postop_room:5009"


@app.route("/schedule-surgery", methods=["POST"])
def schedule_surgery():
    data = request.json
    patient_id = data.get("patient_id")
    blood_units = data.get("blood_units", 0)
    requires_icu = data.get("requires_icu", False)

    successful_steps = []

    try:
        # Paso 1: Validar Paciente
        res = requests.post(
            f"{PATIENT_VALIDATION_URL}/validate",
            json={"patient_id": patient_id},
            timeout=5,
        )
        if res.status_code != 200:
            raise Exception(f"Patient validation failed: {res.json().get('message')}")
        successful_steps.append("patient_validation")

        # Paso 2: Asignar Doctor
        res = requests.post(
            f"{DOCTOR_ASSIGNMENT_URL}/assign",
            json={
                "patient_id": patient_id,
                "surgery_type": data.get("surgery_type"),
                "surgery_day": data.get("surgery_day"),
            },
            timeout=5,
        )
        if res.status_code != 200:
            raise Exception(f"Doctor assignment failed: {res.json().get('message')}")
        successful_steps.append("doctor_assignment")

        # Paso 3: Reservar Sala de Operaciones
        res = requests.post(
            f"{OPERATING_ROOM_URL}/reserve",
            json={
                "patient_id": patient_id,
                "surgery_type": data.get("surgery_type"),
                "surgery_day": data.get("surgery_day"),
            },
            timeout=5,
        )
        if res.status_code != 200:
            raise Exception(
                f"Operating room reservation failed: {res.json().get('message')}"
            )
        successful_steps.append("operating_room")

        # Paso 4: Asignar Anestesiólogo
        res = requests.post(
            f"{ANESTHESIA_URL}/assign",
            json={
                "patient_id": patient_id,
                "anesthesia_type": data.get("anesthesia_type", "general"),
                "surgery_day": data.get("surgery_day"),
            },
            timeout=5,
        )
        if res.status_code != 200:
            raise Exception(
                f"Anesthesia assignment failed: {res.json().get('message')}"
            )
        successful_steps.append("anesthesia")

        # Paso 5: Validar Exámenes de Laboratorio
        res = requests.post(
            f"{LAB_TESTS_URL}/validate", json={"patient_id": patient_id}, timeout=5
        )
        if res.status_code != 200:
            raise Exception(f"Lab tests validation failed: {res.json().get('message')}")
        successful_steps.append("lab_tests")

        # Paso 6: Reservar Medicamentos
        res = requests.post(
            f"{PHARMACY_URL}/reserve",
            json={"patient_id": patient_id, "surgery_type": data.get("surgery_type")},
            timeout=5,
        )
        if res.status_code != 200:
            raise Exception(f"Pharmacy reservation failed: {res.json().get('message')}")
        successful_steps.append("pharmacy")

        # Paso 7: Reservar Sangre (condicional)
        if blood_units > 0:
            res = requests.post(
                f"{BLOOD_BANK_URL}/reserve",
                json={
                    "patient_id": patient_id,
                    "blood_type": data.get("blood_type"),
                    "blood_units": blood_units,
                },
                timeout=5,
            )
            if res.status_code != 200:
                raise Exception(
                    f"Blood bank reservation failed: {res.json().get('message')}"
                )
            successful_steps.append("blood_bank")

        # Paso 8: Asignar Personal de Enfermería
        res = requests.post(
            f"{NURSING_STAFF_URL}/assign",
            json={"patient_id": patient_id, "shift": data.get("shift", "morning")},
            timeout=5,
        )
        if res.status_code != 200:
            raise Exception(
                f"Nursing staff assignment failed: {res.json().get('message')}"
            )
        successful_steps.append("nursing_staff")

        # Paso 9: Reservar Sala Post-Operatoria (condicional por tipo)
        room_type = "icu" if requires_icu else "recovery"
        res = requests.post(
            f"{POSTOP_ROOM_URL}/reserve",
            json={
                "patient_id": patient_id,
                "room_type": room_type,
                "surgery_day": data.get("surgery_day"),
            },
            timeout=5,
        )
        if res.status_code != 200:
            raise Exception(
                f"Post-op room reservation failed: {res.json().get('message')}"
            )
        successful_steps.append("postop_room")

        return jsonify(
            {
                "status": "success",
                "message": f"Surgery scheduled successfully for patient {patient_id}",
                "patient_id": patient_id,
                "steps_completed": successful_steps,
            }
        ), 200

    except Exception as e:
        # Ejecutar compensaciones en orden inverso
        compensate(patient_id, successful_steps[::-1])

        return jsonify(
            {
                "status": "failed",
                "message": str(e),
                "patient_id": patient_id,
                "steps_completed": successful_steps,
                "compensations_executed": successful_steps[::-1],
            }
        ), 500


def compensate(patient_id, steps):
    """Ejecuta compensaciones en orden inverso."""
    compensation_map = {
        "postop_room": (POSTOP_ROOM_URL, "/cancel"),
        "nursing_staff": (NURSING_STAFF_URL, "/cancel"),
        "blood_bank": (BLOOD_BANK_URL, "/cancel"),
        "pharmacy": (PHARMACY_URL, "/cancel"),
        "lab_tests": (LAB_TESTS_URL, "/cancel-validation"),
        "anesthesia": (ANESTHESIA_URL, "/cancel"),
        "operating_room": (OPERATING_ROOM_URL, "/cancel"),
        "doctor_assignment": (DOCTOR_ASSIGNMENT_URL, "/cancel"),
        "patient_validation": (PATIENT_VALIDATION_URL, "/cancel-validation"),
    }

    for step in steps:
        if step in compensation_map:
            url, endpoint = compensation_map[step]
            try:
                requests.post(
                    f"{url}{endpoint}", json={"patient_id": patient_id}, timeout=5
                )
            except Exception:
                pass  # Continue compensating even if one fails


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "orchestrator"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
