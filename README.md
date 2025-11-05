# Saga pattern example

## execution with docker-compose

```bash
docker compose up --build
```

## Example peticion

```bash
curl -X POST localhost:5000/schedule-surgery \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "1",
    "surgery_type": "cardiologia",
    "surgery_day": "monday",
    "shift": "morning",
    "estimated_duration": 120,
    "requires_icu": false,
    "blood_type": "O+",
    "blood_units": 0,
    "anesthesia_type": "regional"
  }'
```


<!-- Inicio doctor-assign Service -->

# Doctor Assign Service

This service manages the assignment of patients to available doctors.

## Endpoints

---

### **POST** `/assign`

Assigns a patient to an available doctor.

**Logic:**
- Looks for a doctor based on the required specialty
- If no doctor with the requested specialty is available, assigns a random available doctor
- Returns the assigned doctor and specialty

**Expected Response:**
- Assigned doctor
- Specialty

---

### **POST** `/cancel`

Cancels an existing doctor–patient assignment.

**Logic:**
- Searches for an active assignment using `patient_id`
- If an assignment exists, it is cancelled
- The doctor’s availability status is updated to `available = true`

---

### **GET** `/health`

Simple endpoint for service health checks.

**Purpose:**
- Confirms that the container/service is running

---

## Summary

| Endpoint     | Method | Description |
|--------------|--------|-------------|
| `/assign`    | POST   | Assigns patient to an available doctor |
| `/cancel`    | POST   | Cancels patient–doctor assignment and frees doctor |
| `/health`    | GET    | Health/heartbeat check |

---

## Notes
- Handles doctor availability logic
- Falls back to random doctor assignment if specialty match not found

<!-- Fin doctor-assign Service -->


