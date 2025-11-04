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
