const express = require("express");
const bodyParser = require("body-parser");

const app = express();
app.use(bodyParser.json());

// Base de datos en memoria
const pacientes = [
  { id: 1, nombre: "Juan Pérez", deuda: 0, contactoEmergencia: "Maria Pérez" },
  {
    id: 2,
    nombre: "Ana Torres",
    deuda: 200,
    contactoEmergencia: "Carlos Torres",
  },
  { id: 3, nombre: "Luis Gómez", deuda: 0, contactoEmergencia: null },
  { id: 4, nombre: "Sara Ruiz", deuda: 0, contactoEmergencia: "Laura Ruiz" },
];

// Pacientes validados con éxito (para poder revertir)
let validacionesExitosas = [];

// Endpoint: Validar paciente
app.post("/validate", (req, res) => {
  const { patient_id } = req.body;
  const id = Number(patient_id);

  const paciente = pacientes.find((p) => p.id === id);
  if (!paciente) {
    return res
      .status(404)
      .json({ message: `Paciente ${patient_id} no encontrado` });
  }

  if (paciente.deuda > 0) {
    return res.status(400).json({
      message: `Paciente ${paciente.nombre} tiene una deuda pendiente`,
    });
  }

  if (!paciente.contactoEmergencia) {
    return res.status(400).json({
      message: `Paciente ${paciente.nombre} no tiene contacto de emergencia`,
    });
  }

  validacionesExitosas.push(patient_id);
  console.log(`✅ Paciente ${paciente.nombre} validado correctamente`);
  res
    .status(200)
    .json({ message: `Paciente ${paciente.nombre} validado correctamente` });
});

// Endpoint: Cancelar validación (para rollback)
app.post("/cancel-validation", (req, res) => {
  const { patient_id } = req.body;
  const index = validacionesExitosas.indexOf(patient_id);

  if (index !== -1) {
    validacionesExitosas.splice(index, 1);
    console.log(`❌ Validación cancelada para paciente ${patient_id}`);
    res
      .status(200)
      .json({ message: `Validación cancelada para paciente ${patient_id}` });
  } else {
    res.status(404).json({
      message: `No hay validación activa para paciente ${patient_id}`,
    });
  }
});

// Endpoint: health check
app.get("/health", (req, res) => {
  res.status(200).json({ status: "healthy", service: "patient-validation" });
});

const PORT = 5001;
app.listen(PORT, () => {
  console.log(`🏥 Patient Validation Service listening on port ${PORT}`);
});
