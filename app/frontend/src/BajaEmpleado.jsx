import { useState } from 'react'

function BajaEmpleado({ empleado, onConfirmada, onCancelar }) {
  const [fechaBaja, setFechaBaja] = useState('')
  const [mensajeError, setMensajeError] = useState('')

  const confirmar = async (evento) => {
    evento.preventDefault()
    setMensajeError('')

    try {
      const respuesta = await fetch(`/api/empleados/${empleado.id}/baja`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fecha_baja: fechaBaja }),
      })
      const cuerpo = await respuesta.json()

      if (!respuesta.ok) {
        setMensajeError(cuerpo.detail || 'No se pudo dar de baja al empleado')
        return
      }

      onConfirmada?.(`Empleado ${cuerpo.numero_empleado} dado de baja con éxito`)
    } catch {
      setMensajeError('No se pudo contactar al servidor')
    }
  }

  return (
    <form onSubmit={confirmar}>
      <h2>Dar de baja a {empleado.numero_empleado}</h2>

      <label htmlFor="empleado-fecha-baja">Fecha de baja</label>
      <input
        id="empleado-fecha-baja"
        data-testid="empleado-fecha-baja"
        type="date"
        value={fechaBaja}
        onChange={(evento) => setFechaBaja(evento.target.value)}
        required
      />

      <button type="submit" data-testid="confirmar-baja">
        Confirmar baja
      </button>
      <button type="button" onClick={onCancelar}>
        Cancelar
      </button>

      {mensajeError && <p data-testid="mensaje-error">{mensajeError}</p>}
    </form>
  )
}

export default BajaEmpleado
