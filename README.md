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

--------------------------------------------------
## Start patient-validation

The service is composed of a list of patients (in-memory database) that will be used for validation, as well as three routes (APIs), which are:

#### **POST** `/validate`

Request used to validate certain patient data.  
To perform this operation, the request body must include the patient's ID as `patient_id`.

The patient ID must meet the following conditions:

1. The ID must belong to a patient in the list (in-memory database).  
2. If the patient exists, they must not have any outstanding debts.  
3. If the patient exists, they must have an emergency contact.

If all three conditions are met, the patient ID is added to a list of successful validations, and a response is returned to the user notifying that the patient was successfully validated.

#### **POST** `/cancel-validation`

Request used to remove the patient ID from the list of successful validations, if the patient ID exists in that list.  
To perform this operation, the request body must include the patient's ID as `patient_id`.

The system validates whether the ID exists in the list.  
If it does, it is removed. Otherwise, the user is notified that there is no active validation for that patient.

#### **GET** `/health`
Request used to check the patient’s health status.

## END patient-validation 
-----------------------------------------------

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

<!-- Inicio medicine Service -->

# Medicine Service

This service manages the reservation and cancellation of hospital medicines required for surgeries.

## Endpoints

---

### **POST** `/reserve`

Reserves the medicines required for a specific surgery type.

**Logic:**
- Validates the presence of `patient_id` and `surgery_type`
- Checks if the specified surgery type has predefined medicine requirements
- Verifies that all required medicines are available in the hospital inventory
- Creates a reservation if all medicines are available
- If the surgery type does not require special medicines, returns an informative message

**Expected Response:**
- Confirmation message of successful reservation
- List of reserved medicines

---

### **POST** `/cancel`

Cancels a medicine reservation for a patient.

**Logic:**
- Searches for an active reservation using `patient_id`
- If a reservation exists, it is removed
- Returns a confirmation message
- If not found, returns a message indicating that no active reservation exists

---

### **GET** `/health`

Simple endpoint for service health checks.

**Purpose:**
- Confirms that the container/service is running properly

---

## Summary

| Endpoint     | Method | Description |
|--------------|--------|-------------|
| `/reserve`   | POST   | Reserves medicines required for a surgery |
| `/cancel`    | POST   | Cancels an existing medicine reservation |
| `/health`    | GET    | Health/heartbeat check |

---

## Notes
- Handles medicine reservation and cancellation logic  
- Ensures required medicines are available before surgeries  
- Returns clear messages for both success and error cases  

<!-- Fin medicine Service -->

<!-- Inicio nursing Service -->

# Nursing Service

This service manages the assignment of available nurses to patients based on shift requirements.

## Endpoints

---

### **POST** `/assign`

Assigns an available nurse to a patient for a specific shift.

**Logic:**
- Requires `patient_id` and optionally `shift` (defaults to "morning") in the request body.
- Checks for available nurses in the specified shift.
- If available, assigns the first nurse and removes them from the available list.
- If not available, returns an error message.

**Example Request:**

curl -X POST localhost:5008/assign \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "123", "shift": "morning"}'

**Expected Responses:**

`200 OK`
```json
{
  "message": "Nurse Ana assigned to patient 123 for morning shift",
  "assignment": {
    "patient_id": "123",
    "nurse": "Ana",
    "shift": "morning"
  }
}
```

`400 Bad Request`
```json
{
  "message": "Missing patient_id"
}
```

**or**
```json
{
  "message": "No nurses available for morning shift"
}
```

---

### **POST** `/cancel`

Cancels an existing nurse assignment for a given patient.

**Logic:**
- Requires `patient_id` in the request body.
- Searches for the patient's active assignment.
- If found, removes it and restores the nurse to the available list.
- If not found, returns an informative message.

**Example Request:**

curl -X POST localhost:5008/cancel \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "123"}'

**Expected Responses:**

`200 OK`
```json
{
  "message": "Assignment for patient 123 rolled back",
  "restored_nurse": "Ana"
}
```

`400 Bad Request`
```json
{
  "message": "Missing patient_id"
}
```

`404 Not Found`
```json
{
  "message": "No assignment found for patient 123"
}
```

---

### **GET** `/health`

Simple endpoint to check the service status.

**Purpose:**
- Confirms that the service is running and operational.

**Expected Response:**
```json
{
  "status": "ok",
  "service": "nursing"
}
```

---

## Summary

| Endpoint  | Method | Description                                    |
|-----------|--------|------------------------------------------------|
| /assign   | POST   | Assigns a nurse to a patient for a given shift |
| /cancel   | POST   | Cancels a nurse–patient assignment             |
| /health   | GET    | Health/heartbeat check                         |

---

## Notes

- Uses an in-memory database of nurses per shift.
- Automatically updates nurse availability after each assignment or cancellation.
- Provides clear and consistent success/error messages.
- Designed for integration within a Saga pattern for surgery scheduling systems.

## Available Shifts

- `morning` - Morning shift (Ana, Carlos)
- `evening` - Evening shift (Beatriz, David)
- `night` - Night shift (Elena)

<!-- Fin nursing Service -->

<!-- Inicio anesthesia Service -->

# Anesthesia Service

This service manages the assignment and cancellation of anesthesiologists for surgeries, based on their type of anesthesia and daily availability.

## Endpoints

---

### **POST** `/assign`

Assigns an available anesthesiologist to a patient based on the required anesthesia type and surgery day.

**Logic:**
- Validates the presence of `patient_id`, `anesthesia_type`, and `surgery_day`.
- Searches for an anesthesiologist who can perform the specified type of anesthesia and is available on the given day.
- If found, marks the anesthesiologist as unavailable for that day and saves the assignment.
- If no anesthesiologist matches the conditions, a conflict message is returned.

**Expected Response:**
- Success message confirming the assigned anesthesiologist.
- On error, returns a message indicating missing data or unavailability.

---

### **POST** `/cancel`

Cancels an existing anesthesiologist assignment for a specific patient.

**Logic:**
- Validates the presence of `patient_id`.
- Searches for an active assignment linked to that patient.
- If found, removes the assignment and restores the anesthesiologist’s availability for that day.
- If no assignment exists, returns a not found message.

**Expected Response:**
- Confirmation message of cancellation.
- Informative error message when no active assignment is found.

---

### **GET** `/health`

Simple endpoint for checking service health.

**Purpose:**
- Confirms that the service is running and operational.

---

## Summary

| Endpoint    | Method | Description |
|--------------|--------|-------------|
| `/assign`    | POST   | Assigns an anesthesiologist to a patient |
| `/cancel`    | POST   | Cancels an existing anesthesiologist assignment |
| `/health`    | GET    | Health/heartbeat check |

---

## Notes
- Uses an in-memory database of anesthesiologists with their skills and availability.  
- Prevents assigning the same anesthesiologist twice on the same day.  
- Provides clear and consistent messages for both success and error cases.  
- Suitable for integration with surgery scheduling systems or hospital management services.

<!-- Fin anesthesia Service -->

---

# Bloods

This service manages the reservation and cancellation of blood units for patients who require transfusions during surgery. It also maintains an inventory of blood types and available units, as well as a temporary record of active reserves.

## Endpoints


### **POST** `/reserve`

Reserve blood units for a specific patient.

- Requires the fields `patient_id`, `blood_type`, and `blood_units` in the request body.
- Normalizes the blood type and validates its existence in the inventory.
- Verifies that there are enough units available for the requested type.
- If the conditions are met, deducts the units from the inventory and saves the reservation associated with the patient.

**Expected Response:**

`200`
```json
{
  "patient_id": "123",
  "status": "reserved",
  "message": "Reservadas 2 unidades de sangre tipo O+"
}
```

`400`
```json
{
  "patient_id": "123",
  "status": "not_available",
  "message": "No hay suficientes unidades (1 disponibles, 3 requeridas)"
}
```

`400`
```json
{
  "status": "error",
  "message": "Datos incompletos"
}
```

`404`
```json
{
  "patient_id:": "123",
  "status": "error",
  "message": "Tipo de sangre ABX no disponible"
}
```

---

### **POST** `/cancel`

Cancel a previously made blood reservation.

- Requires `patient_id` in the request body.
- Checks if there is an active reservation for that patient.
- If found, restores the units to inventory and deletes the reservation record.
- If not found, returns an error message.


**Expected Response:**

`200`
```json
{
  "patient_id": "123",
  "status": "canceled",
  "message": "Reserva cancelada y 2 unidades devueltas al inventario (O+)"
}
```

`404`
```json
{
  "status": "error",
  "message": "No hay reserva previa para este paciente"
}
```

---


### **GET** `/health`

Simple endpoint to check the service status.

**Expected Response:**
`200`
```json
{
  "status": "ok",
  "service": "blood-bank"
}
```
---

## Summary

| Endpoint    | Method | Descripción                                      |
|-------------|--------|--------------------------------------------------|
| `/reserve`  | POST   | Reserve blood units for a patient                |
| `/cancel`   | POST   | Cancel a reservation and return units to stock   |
| `/health`   | GET    | Check service status                             |

---
