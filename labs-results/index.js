const express = require("express");
const bodyParser = require("body-parser");

const app = express();
app.use(express.json());

// 🧠 Base de datos en memoria: resultados de laboratorio
const labResults = [
  { patient_id: 1, hemoglobin: 13.5, glucose: 95 },
  { patient_id: 2, hemoglobin: 8.9, glucose: 110 },
  { patient_id: 3, hemoglobin: 12.0, glucose: 190 },
  { patient_id: 4, hemoglobin: 11.2, glucose: 130 },
];

// 📋 Historial de verificaciones realizadas (para poder revertir)
const checksPerformed = new Set();

// 🏥 Endpoint de salud
app.get("/health", (req, res) => {
  res.json({ status: "ok", service: "lab" });
});

// ✅ Endpoint principal: verificar si el paciente es apto
app.post("/validate", (req, res) => {
  const { patient_id } = req.body;

  const patient = labResults.find((p) => p.patient_id === Number(patient_id));
  if (!patient) {
    return res
      .status(404)
      .json({ status: "error", message: "Paciente no encontrado" });
  }

  const { hemoglobin, glucose } = patient;

  // Guardar que este paciente fue evaluado (para posible rollback)
  checksPerformed.add(patient_id);

  if (hemoglobin < 10) {
    return res.json({
      patient_id,
      status: "not_fit",
      reason: "Hemoglobina demasiado baja",
    });
  }

  if (glucose > 180) {
    return res.json({
      patient_id,
      status: "not_fit",
      reason: "Glucosa demasiado alta",
    });
  }

  return res.json({
    patient_id,
    status: "fit",
    message: "Paciente apto para cirugía",
  });
});

// 🔁 Endpoint de cancelación (rollback)
app.post("/cancel-validation", (req, res) => {
  const { patient_id } = req.body;

  if (!checksPerformed.has(patient_id)) {
    return res.status(404).json({
      status: "error",
      message: "No se encontró una validación previa para revertir",
    });
  }

  // Eliminar el registro de verificación (simula deshacer la validación)
  checksPerformed.delete(patient_id);

  return res.json({
    patient_id,
    status: "canceled",
    message: "Verificación de laboratorio revertida exitosamente",
  });
});

// 🚀 Iniciar servidor
const PORT = 5005;
app.listen(PORT, () =>
  console.log(`🧪 Lab service corriendo en puerto ${PORT}`),
);
