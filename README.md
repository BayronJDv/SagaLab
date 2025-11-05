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


