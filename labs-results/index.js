const express = require('express');

const app = express();
app.use(express.json());

/**
 * Base de datos en memoria que almacena los resultados de laboratorio de los pacientes.
 * Contiene información de hemoglobina y glucosa para cada paciente.
 * @type {Array<{patient_id: number, hemoglobin: number, glucose: number}>}
 */
const labResults = [
  { patient_id: 1, hemoglobin: 13.5, glucose: 95 },
  { patient_id: 2, hemoglobin: 8.9, glucose: 110 },
  { patient_id: 3, hemoglobin: 12.0, glucose: 190 },
  { patient_id: 4, hemoglobin: 11.2, glucose: 130 },
];

/**
 * Historial de verificaciones realizadas.
 * Almacena los IDs de pacientes que han sido evaluados para poder revertir la operación si es necesario.
 * @type {Set<number>}
 */
const checksPerformed = new Set();

/**
 * Endpoint de verificación de salud del servicio.
 * @route GET /health
 * @returns {Object} 200 - Estado del servicio
 * @returns {string} 200.status - Estado del servicio (ok)
 * @returns {string} 200.service - Nombre del servicio (lab)
 */
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'lab' });
});

/**
 * Endpoint principal para validar si un paciente es apto para cirugía.
 * Verifica los niveles de hemoglobina y glucosa del paciente.
 *
 * Criterios de aptitud:
 * - Hemoglobina debe ser >= 10
 * - Glucosa debe ser <= 180
 *
 * @route POST /validate
 * @param {Object} req.body - Datos de la solicitud
 * @param {number} req.body.patient_id - ID del paciente a validar
 * @returns {Object} 200 - Resultado de la validación
 * @returns {number} 200.patient_id - ID del paciente
 * @returns {string} 200.status - Estado de la validación (fit/not_fit)
 * @returns {string} 200.reason - Razón por la cual no es apto (si aplica)
 * @returns {string} 200.message - Mensaje de confirmación (si es apto)
 * @returns {Object} 404 - Paciente no encontrado
 */
app.post('/validate', (req, res) => {
  const { patient_id } = req.body;

  const patient = labResults.find((p) => p.patient_id === Number(patient_id));
  if (!patient) {
    return res
      .status(404)
      .json({ status: 'error', message: 'Paciente no encontrado' });
  }

  const { hemoglobin, glucose } = patient;

  // Guardar que este paciente fue evaluado (para posible rollback)
  // Guardar que este paciente fue evaluado (para posible rollback)
  checksPerformed.add(Number(patient_id));
  if (hemoglobin < 10) {
    return res.json({
      patient_id,
      status: 'not_fit',
      reason: 'Hemoglobina demasiado baja',
    });
  }

  if (glucose > 180) {
    return res.json({
      patient_id,
      status: 'not_fit',
      reason: 'Glucosa demasiado alta',
    });
  }

  return res.json({
    patient_id,
    status: 'fit',
    message: 'Paciente apto para cirugía',
  });
});

/**
 * Endpoint de cancelación (rollback) de una validación.
 * Revierte la verificación realizada a un paciente, eliminando su registro
 * del historial de verificaciones realizadas.
 *
 * @route POST /cancel-validation
 * @param {Object} req.body - Datos de la solicitud
 * @param {number} req.body.patient_id - ID del paciente cuya validación se debe cancelar
 * @returns {Object} 200 - Confirmación de cancelación exitosa
 * @returns {number} 200.patient_id - ID del paciente
 * @returns {string} 200.status - Estado de la operación (canceled)
 * @returns {string} 200.message - Mensaje de confirmación
 * @returns {Object} 404 - No se encontró una validación previa para revertir
 */
app.post('/cancel-validation', (req, res) => {
  const { patient_id } = req.body;

  if (!checksPerformed.has(patient_id)) {
    return res.status(404).json({
      status: 'error',
      message: 'No se encontró una validación previa para revertir',
    });
  }

  // Eliminar el registro de verificación (simula deshacer la validación)
  checksPerformed.delete(patient_id);

  return res.json({
    patient_id,
    status: 'canceled',
    message: 'Verificación de laboratorio revertida exitosamente',
  });
});

/**
 * Inicialización del servidor Express.
 * El servicio de laboratorio escucha en el puerto 5005.
 */
const PORT = 5005;
app.listen(PORT, () => console.log(`Lab service corriendo en puerto ${PORT}`));

// post http://localhost:5005/validate {"patient_id": 1}
