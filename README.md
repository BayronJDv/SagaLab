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

---

#### **POST** `/validate`

Request used to validate certain patient data.  
To perform this operation, the request body must include the patient's ID as `patient_id`.

The patient ID must meet the following conditions:

1. The ID must belong to a patient in the list (in-memory database).  
2. If the patient exists, they must not have any outstanding debts.  
3. If the patient exists, they must have an emergency contact.

If all three conditions are met, the patient ID is added to a list of successful validations, and a response is returned to the user notifying that the patient was successfully validated.

---

#### **POST** `/cancel-validation`

Request used to remove the patient ID from the list of successful validations, if the patient ID exists in that list.  
To perform this operation, the request body must include the patient's ID as `patient_id`.

The system validates whether the ID exists in the list.  
If it does, it is removed. Otherwise, the user is notified that there is no active validation for that patient.

---

#### **GET** `/health`
Request used to check the patient’s health status.

## END patient-validation 
-----------------------------------------------