const express = require("express");
const bodyParser = require("body-parser");

const app = express();
app.use(bodyParser.json());

// Base de datos en memoria
// Cada anestesiólogo tiene: id, nombre, tipos de anestesia que puede aplicar, y disponibilidad por día
const anesthesiologists = [
  {
    id: 1,
    name: "Dr. Jiménez",
    types: ["general", "regional"],
    availability: { monday: true, tuesday: false, wednesday: true },
  },
  {
    id: 2,
    name: "Dra. Vargas",
    types: ["local", "general"],
    availability: { monday: true, tuesday: true, wednesday: false },
  },
  {
    id: 3,
    name: "Dr. Mendoza",
    types: ["regional"],
    availability: { monday: true, tuesday: true, wednesday: true },
  },
];

const activeAssignments = [];

// Endpoint: asignar anestesiólogo
app.post("/assign", (req, res) => {
  const { patient_id, anesthesia_type, surgery_day } = req.body;

  if (!patient_id || !anesthesia_type || !surgery_day) {
    return res.status(400).json({ message: "Datos incompletos" });
  }

  // Buscar un anestesiólogo que pueda aplicar ese tipo y esté disponible ese día
  const available = anesthesiologists.find(
    (a) => a.types.includes(anesthesia_type) && a.availability[surgery_day],
  );

  if (!available) {
    console.log(
      `❌ No hay anestesiólogos disponibles para ${anesthesia_type} el día ${surgery_day}`,
    );
    return res.status(409).json({
      message: `No hay anestesiólogos disponibles para ${anesthesia_type} el día ${surgery_day}`,
    });
  }

  // Marcar como ocupado ese día
  available.availability[surgery_day] = false;

  // Registrar la asignación
  activeAssignments.push({
    patient_id,
    anesthesiologist_id: available.id,
    day: surgery_day,
  });

  console.log(
    `💉 Anestesiólogo ${available.name} asignado al paciente ${patient_id} (${anesthesia_type})`,
  );
  return res.status(200).json({
    message: `Anestesiólogo ${available.name} asignado correctamente al paciente ${patient_id}`,
  });
});

// Endpoint: cancelar asignación
app.post("/cancel", (req, res) => {
  const { patient_id } = req.body;

  if (!patient_id) {
    return res.status(400).json({ message: "Falta patient_id" });
  }

  const assignment = activeAssignments.find((a) => a.patient_id === patient_id);

  if (!assignment) {
    return res
      .status(404)
      .json({
        message: `No se encontró asignación para paciente ${patient_id}`,
      });
  }

  // Liberar disponibilidad del anestesiólogo
  const anesth = anesthesiologists.find(
    (a) => a.id === assignment.anesthesiologist_id,
  );
  if (anesth) {
    anesth.availability[assignment.day] = true;
  }

  // Eliminar asignación
  const index = activeAssignments.indexOf(assignment);
  activeAssignments.splice(index, 1);

  console.log(
    `❌ Asignación cancelada para paciente ${patient_id}, anestesiólogo ${anesth.name}`,
  );
  return res
    .status(200)
    .json({ message: `Asignación cancelada para paciente ${patient_id}` });
});

// Endpoint: health check
app.get("/health", (req, res) => {
  res.status(200).json({ status: "healthy", service: "anesthesia" });
});

const PORT = 5004;
app.listen(PORT, () => {
  console.log(`💉 Anesthesia Service listening on port ${PORT}`);
});
