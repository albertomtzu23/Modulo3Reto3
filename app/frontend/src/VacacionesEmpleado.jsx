import { useEffect, useState } from 'react'

function VacacionesEmpleado({ empleado, onCerrar }) {
  const anioConsulta = new Date().getFullYear()
  const [fechaInicio, setFechaInicio] = useState('')
  const [fechaFin, setFechaFin] = useState('')
  const [diasDisponibles, setDiasDisponibles] = useState(null)
  const [mensaje, setMensaje] = useState('')

  const cargarSaldo = () => {
    fetch(`/api/empleados/${empleado.id}/vacaciones?anio=${anioConsulta}`)
      .then((respuesta) => respuesta.json())
      .then((datos) => setDiasDisponibles(datos.dias_disponibles))
      .catch(() => setDiasDisponibles(null))
  }

  useEffect(cargarSaldo, [empleado.id])

  const enviar = async (evento) => {
    evento.preventDefault()
    setMensaje('')

    try {
      const respuesta = await fetch(`/api/empleados/${empleado.id}/vacaciones`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fecha_inicio: fechaInicio, fecha_fin: fechaFin }),
      })
      const cuerpo = await respuesta.json()

      if (!respuesta.ok) {
        setMensaje(cuerpo.detail || 'No se pudo registrar la solicitud')
        return
      }

      const anioSolicitud = fechaInicio.slice(0, 4)
      setMensaje(
        `Solicitud registrada: ${cuerpo.dias_habiles} días hábiles. ` +
          `Te quedan ${cuerpo.dias_restantes} días hábiles en ${anioSolicitud}.`
      )
      cargarSaldo()
    } catch {
      setMensaje('No se pudo contactar al servidor')
    }
  }

  return (
    <form onSubmit={enviar}>
      <h2>Vacaciones de {empleado.numero_empleado}</h2>

      <p>
        Días disponibles en {anioConsulta}:{' '}
        <span data-testid="vacaciones-disponibles">{diasDisponibles ?? '...'}</span>
      </p>

      <label htmlFor="vacaciones-fecha-inicio">Fecha de inicio</label>
      <input
        id="vacaciones-fecha-inicio"
        data-testid="vacaciones-fecha-inicio"
        type="date"
        value={fechaInicio}
        onChange={(evento) => setFechaInicio(evento.target.value)}
        required
      />

      <label htmlFor="vacaciones-fecha-fin">Fecha de fin</label>
      <input
        id="vacaciones-fecha-fin"
        data-testid="vacaciones-fecha-fin"
        type="date"
        value={fechaFin}
        onChange={(evento) => setFechaFin(evento.target.value)}
        required
      />

      <button type="submit" data-testid="vacaciones-enviar">
        Enviar solicitud
      </button>
      <button type="button" onClick={onCerrar}>
        Cerrar
      </button>

      {mensaje && <p data-testid="vacaciones-mensaje">{mensaje}</p>}
    </form>
  )
}

export default VacacionesEmpleado
