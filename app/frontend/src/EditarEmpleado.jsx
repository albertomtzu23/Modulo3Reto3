import { useEffect, useState } from 'react'

function EditarEmpleado({ empleado, onGuardado, onCancelar }) {
  const [departamentos, setDepartamentos] = useState([])
  const [puesto, setPuesto] = useState(empleado.puesto)
  const [departamento, setDepartamento] = useState(empleado.departamento)
  const [mensajeExito, setMensajeExito] = useState('')
  const [mensajeError, setMensajeError] = useState('')

  useEffect(() => {
    fetch('/api/departamentos')
      .then((respuesta) => respuesta.json())
      .then(setDepartamentos)
      .catch(() => setDepartamentos([]))
  }, [])

  const guardar = async (evento) => {
    evento.preventDefault()
    setMensajeExito('')
    setMensajeError('')

    try {
      const respuesta = await fetch(`/api/empleados/${empleado.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ puesto, departamento }),
      })
      const cuerpo = await respuesta.json()

      if (!respuesta.ok) {
        setMensajeError(cuerpo.detail || 'No se pudo editar al empleado')
        return
      }

      setMensajeExito(`Empleado ${cuerpo.numero_empleado} actualizado con éxito`)
      onGuardado?.()
    } catch {
      setMensajeError('No se pudo contactar al servidor')
    }
  }

  return (
    <form onSubmit={guardar}>
      <h2>Editar empleado {empleado.numero_empleado}</h2>

      <label htmlFor="empleado-puesto">Puesto</label>
      <input
        id="empleado-puesto"
        data-testid="empleado-puesto"
        type="text"
        value={puesto}
        onChange={(evento) => setPuesto(evento.target.value)}
        required
      />

      <label htmlFor="empleado-departamento">Departamento</label>
      <select
        id="empleado-departamento"
        data-testid="empleado-departamento"
        value={departamento}
        onChange={(evento) => setDepartamento(evento.target.value)}
        required
      >
        {departamentos.map((item) => (
          <option key={item} value={item}>
            {item}
          </option>
        ))}
      </select>

      <button type="submit" data-testid="empleado-guardar">
        Guardar
      </button>
      <button type="button" onClick={onCancelar}>
        Cancelar
      </button>

      {mensajeExito && <p data-testid="mensaje-exito">{mensajeExito}</p>}
      {mensajeError && <p data-testid="mensaje-error">{mensajeError}</p>}
    </form>
  )
}

export default EditarEmpleado
